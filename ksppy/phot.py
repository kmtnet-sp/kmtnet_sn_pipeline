import astropy.io.fits as pyfits
import numpy as np
import os

def fig_to_png(fig, outname):
    from matplotlib.backends.backend_agg import FigureCanvasAgg

    FigureCanvasAgg(fig)
    fig.savefig(outname)


if 0:
    fmt = "fk5; point(%15f, %15f)\n"
    s = [fmt % (ra1, dec1) for ra1, dec1 in zip(ra, dec)[::10]]
    open("test.reg","w").writelines(s)


def get_phot(ra0, dec0, radius0=0.85):
    # ra0, dec0 = center

    print "downloading a csv file"
    url = "https://www.aavso.org/cgi-bin/apass_download.pl?ra=%.4f&dec=%.5f&radius=%.2f&outtype=1" % (ra0, dec0, radius0)

    import urllib2
    s = urllib2.urlopen(url).read()

    return s


def get_phot_file(center, dir):
    try:
        import healpy
    except ImportError:
        healpy = None

    if healpy is not None:
        nside = 1024
        # healpy.max_pixrad(1024)/np.pi*180*60. -> 3.6 # radius
        ipix = healpy.ang2pix(nside,
                              center[0]/180.*np.pi,
                              center[1]/180.*np.pi)

        ra0, dec0 = [f * 180. / np.pi for f in healpy.pix2ang(nside, ipix)]
        if dec0 > 180:
            dec0 = - (360 - dec0)
        radius0 = 0.85

        phot_name0 = "apass_%d_%d_%.4f_%.5f.csv" % (nside, ipix, ra0, dec0)
    else:
        ra0, dec0 = center
        phot_name0 = "apass_%.4f_%.5f.csv" % (ra0, dec0)
        radius0 = 0.85


    import os
    phot_name = os.path.join(dir, phot_name0)

    if not os.path.exists(phot_name):
        s = get_phot(ra0, dec0, radius0)
        open(phot_name, "w").write(s)

    return phot_name


band_keys = dict(V=("Johnson_V", "Verr"),
                 B=("Johnson_B", "B_err"),
                 g=("Sloan_g", "gerr"),
                 r=("Sloan_r", "r_err"),
                 i=("Sloan_i", "i_err"))


def extract_header_from_cat(cat):
    d = cat[1].data["Field Header Card"][0]
    cards = [pyfits.Card.fromstring(l) for l in d]
    header = pyfits.Header(cards=cards)
    return header


def get_nh_wcs(fits_name):
    if fits_name.endswith(".fz"):
        extnum = 1
    else:
        extnum = 0

    fits = pyfits.open(fits_name)
    from astropy.wcs import WCS
    wcs = WCS(fits[extnum].header)

    return wcs


def update_cat_coord(cat_name, fits_name, outcat_name):
    cat = pyfits.open(cat_name)

    wcs = get_nh_wcs(fits_name)

    x = cat[2].data["XWIN_IMAGE"]
    y = cat[2].data["YWIN_IMAGE"]

    ra, dec = wcs.all_pix2world(x, y, 1)

    cat[2].data["X_WORLD"][:] = ra
    cat[2].data["Y_WORLD"][:] = dec

    cat.writeto(outcat_name, clobber=True)


def load_magzpt(magzpt_name):
    l = open(magzpt_name).readlines()
    d = dict()
    for l1 in l:
        l1s = l1.strip()
        if l1s.startswith("#"):
            continue
        k, v = l1s.split("=")
        d[k] = float(v)
    return d


def apply_flux_cal(magzpt_dict, x, y, mag_inst):
    cx, cy = magzpt_dict["PHOTCP1"], magzpt_dict["PHOTCP2"]
    magzp, magzp_r2 = magzpt_dict["MAGZP"], magzpt_dict["MAGZPR2"]

    R = ((x-cx)**2 + (y-cy)**2)**.5
    mag_phot = mag_inst + magzp + R**2 * magzp_r2

    return mag_phot


def update_cat_mag(cat_name, magzpt_name, outcat_name):

    magzpt_dict = load_magzpt(magzpt_name)

    cat = pyfits.open(cat_name)

    x = cat[2].data["XWIN_IMAGE"]
    y = cat[2].data["YWIN_IMAGE"]
    mag_inst = cat[2].data["MAG_AUTO"]

    mag_phot = apply_flux_cal(magzpt_dict, x, y, mag_inst)
    cat[2].data["MAG_AUTO"] = mag_phot

    cat.writeto(outcat_name, clobber=True)


def do_phot(cat_name, fits_name, band, phot_dir, dir,
            phot_file=None):

    if band not in band_keys:
        raise ValueError("Band %s is not supported." % band)

    cat = pyfits.open(cat_name)

    x = cat[2].data["XWIN_IMAGE"]
    y = cat[2].data["YWIN_IMAGE"]

    wcs = get_nh_wcs(fits_name)

    # radius = (np.sum((footprint - center)**2, axis=1)**.5).max()

    if phot_file is None:

        if hasattr(wcs, "calcFootprint"):
            footprint = wcs.calcFootprint()
        else:
            footprint = wcs.calc_footprint()

        from check_overwrap import get_mean_lonlat
        center = get_mean_lonlat(footprint[:,0], footprint[:,1])
        # footprint.mean(axis=0)
        # print(footprint, center)
        ra0, dec0 = center[0].deg, center[1].deg

        phot_file = get_phot_file((ra0, dec0), phot_dir)

    import pandas as pd
    df = pd.read_csv(phot_file)

    import scipy
    import scipy.spatial
    from scipy.spatial import KDTree
    xx, yy = wcs.all_world2pix(df["radeg"], df["decdeg"], 1)

    if 0:
        fmt = "image; point(%15f, %15f)\n"
        s = [fmt % (ra1, dec1) for ra1, dec1 in zip(xx, yy)[:]]
        open("test.reg","w").writelines(s)

    tree = KDTree(np.array([x, y]).T)
    dist, idx0 = tree.query(np.array([xx, yy]).T)

    msk = dist < 1.5

    idx = idx0[msk]

    inst_mag = cat[2].data["MAG_AUTO"][idx]
    inst_magE = 2.5/np.log(10)*(cat[2].data["FLUXERR_AUTO"]/cat[2].data["FLUX_AUTO"])[idx]

    inst_mag[inst_mag > 90] = np.nan

    mag_name, magE_name = band_keys[band]

    phot_mag = df[mag_name][msk]
    phot_magE = df[magE_name][msk]

    #plot(phot_mag, inst_mag, "o")
    diffmag = phot_mag - inst_mag
    diffmagE = (inst_magE**2 + phot_magE**2)**.5
    diffmag0 = diffmag.copy()

    if band == "B":
        mag_low, mag_up = 17.5, 14.5
    elif band == "V":
        mag_low, mag_up = 15.5, 13.0
    elif band == "i":
        mag_low, mag_up = 16.0, 13.5
    else:
        mag_low, mag_up = 16., 13.5


    diffmag[(phot_mag < mag_up) | (phot_mag > mag_low)] = np.nan

    maskE = (diffmagE > 0.08).values

    #draw_figure1()
    basename = os.path.basename(cat_name)
    outfig1name = os.path.join(dir, basename + ".fig1.png")
    draw_figure1(phot_mag, phot_magE, diffmag, diffmagE, diffmag0, maskE,
                 outfig1name)

    # draw_figure2()

    # #maskE = np.isfinite(diffmag)
    # fig3 = figure(3)
    # ax3 = fig3.add_subplot(111, aspect=1)
    # sc = ax3.scatter(xx[msk][~maskE], yy[msk][~maskE], c=diffmag[~maskE],
    #                  vmin=29.0, vmax=29.5,
    #                  cmap="gist_heat")

    # fig3.colorbar(sc)

    orig_header = extract_header_from_cat(cat)
    #cx, cy = 9481, -467
    cx, cy = orig_header["CRPIX1"], orig_header["CRPIX2"]
    dR = ((xx - cx) ** 2 + (yy - cy) ** 2)**.5

    #errorbar((yy-cy)[msk], diffmag, fmt=".", yerr=diffmagE)


    weight = 10.**(-diffmagE).values

    m_finite = np.isfinite(diffmag.values)
    p = np.polyfit(dR[msk][m_finite]**2, diffmag.values[m_finite], 1, w=weight[m_finite])
    dM = np.polyval(p, dR[msk]**2)

    mag_std = diffmag.values[m_finite].std()

    m_finite = m_finite & (np.abs(diffmag.values - dM) < mag_std * 2)

    p = np.polyfit(dR[msk][m_finite]**2, diffmag.values[m_finite], 1, w=weight[m_finite])
    dM = np.polyval(p, dR[msk]**2)

    outfig2name = os.path.join(dir, basename + ".fig2.png")
    draw_figure2(dR, diffmag, diffmagE, msk, m_finite, p, dM, mag_std,
                 outfig2name)

    r = dict(PHOTCP1=cx, PHOTCP2=cy, MAGZP=p[1], MAGZPR2=p[0])
    return r


def save_phot(fits_name, phot_file):

    wcs = get_nh_wcs(fits_name)

    if hasattr(wcs, "calcFootprint"):
        footprint = wcs.calcFootprint()
    else:
        footprint = wcs.calc_footprint()

    from check_overwrap import get_mean_lonlat
    center = get_mean_lonlat(footprint[:,0], footprint[:,1])
    # footprint.mean(axis=0)
    # print(footprint, center)
    ra0, dec0 = center[0].deg, center[1].deg
    print(ra0, dec0)
    s = get_phot(ra0, dec0, radius0=0.85)

    open(phot_file, "w").write(s)


def save_magzp(r, outname):
    l = []
    for k, v in r.iteritems():
        l.append("%s=%s\n" % (k, v))

    open(outname, "w").writelines(l)


def draw_figure2(dR, diffmag, diffmagE, msk, m_finite, p, dM, mag_std,
                 figname):
    import matplotlib.pyplot as plt
    fig2 = plt.Figure()
    #fig2.clf()
    ax = fig2.add_subplot(211)
    ax2 = fig2.add_subplot(212, sharex=ax)
    ax.errorbar(dR[msk][~m_finite], diffmag.values[~m_finite], fmt=".",
                yerr=diffmagE[~m_finite], color=".5")
    ax.errorbar(dR[msk][m_finite], diffmag.values[m_finite], fmt=".", color="b",
                yerr=diffmagE[m_finite])


    R = np.linspace(dR.min(), dR.max(), 100)
    RM = np.polyval(p, R**2)
    ax.plot(R, RM, "r-")
    ax.set_ylim(p[-1]-3*mag_std, p[-1]+4*mag_std)

    ax2.errorbar(dR[msk][m_finite], (diffmag-dM)[m_finite], fmt=".", yerr=diffmagE[m_finite])

    fig_to_png(fig2, figname)

def draw_figure1(phot_mag, phot_magE, diffmag, diffmagE, diffmag0, maskE,
                 figname):
    import matplotlib.pyplot as plt
    fig1 = plt.Figure()
    ax1 = fig1.add_subplot(111)
    ax1.errorbar(phot_mag, diffmag0, fmt=".",
                 yerr=diffmagE,
                 xerr=phot_magE, color="0.7")
    ax1.errorbar(phot_mag, diffmag, fmt=".",
                 yerr=diffmagE,
                 xerr=phot_magE)

    ax1.errorbar(phot_mag[maskE], diffmag[maskE], fmt="o")

    fig_to_png(fig1, figname)


if 0:
    cat_name = "N2784-4.Q0.B.150211_0626.C.003569.091043N2208.0100_tan.cat"
    fits_name = "N2784-4.Q0.B.150211_0626.C.003569.091043N2208.0100.nh.fits"

    assert cat_name.endswith(".cat")

    band = "B"
    phot_dir = "."
    dir = "."

    if band not in band_keys:
        raise ValueError("Band %s is not supported." % band)

    outcat_name = cat_name.replace(".cat", ".nh.cat")
    update_catalog(cat_name, fits_name, outcat_name)


    do_phot(outcat_name, fits_name, band, phot_dir, dir)

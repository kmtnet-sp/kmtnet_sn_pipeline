import astropy.io.fits as pyfits
import astropy.wcs as pywcs
import os

if 0:
    f = pyfits.open("kmtc.20150329.007590.ne.fits")
    f[0].header["CTYPE1"]  = 'RA---TAN'
    f[0].header["CTYPE2"]  = 'DEC--TAN'
    for pv in ["PV2_1", "PV2_2", "PV2_3"]:
        del f[0].header[pv]
    f.writeto("test2.fits")

def convert_xy(header, x, y):
        """
        convert x, y to flattened coordinate.
        """
        x1 = x - header["CRPIX1"]
        y1 = y - header["CRPIX2"]

        wcs = pywcs.WCS(header)
        #print dir(wcs.wcs)
        #mat = np.matrix(wcs.wcs.piximg_matrix) #pixel_scale_matrix
        if "CDELT1" in header:
            mat = np.matrix([[header["CDELT1"], 0.],
                             [0, header["CDELT2"]]])
        else:
            mat = np.matrix([[header["CD1_1"], 0.],
                             [0, header["CD2_2"]]])

        print mat
        xy2 = mat * (x1, y1)
        x2, y2 = np.array(xy2)
        # y2 = mat[1] * (x1, y1)
        # y2 = header["CD2_1"] * x1 + header["CD2_2"] * y1

        #x2 = np.array([1, 5, 3])/10.
        #y2 = np.array([3, 5, 3])/10.
        if 0:
            clf()
            scatter(x2, y2)

        phi = np.arctan2(y2, x2)
        theta_ = (x2**2 + y2**2)**.5 # in degree
        theta = theta_ * np.pi / 180. # to radian


        theta2 = theta - 33.*theta**3


        to_deg = 180./np.pi
        x3 = theta2 * to_deg * np.cos(phi)
        y3 = theta2 * to_deg * np.sin(phi)

        xy4 = mat.I * (x3, y3)
        x4, y4 = np.array(xy4)

        return x4 + header["CRPIX1"], y4 + header["CRPIX2"]


def undistort_catalog(cat_name, tmpdir):
    import numpy as np

    f = pyfits.open(cat_name)

    #original header
    cards = [pyfits.Card.fromstring(s) for s in f[1].data[0][0]]
    header = pyfits.Header(cards)

    # input x, y coordinates
    d  = f[2].data
    h  = f[2].data
    XKEY, YKEY = "XWIN_IMAGE", "YWIN_IMAGE"
    x, y = d[XKEY], d[YKEY]

    if 0:
        for xx, yy in np.array((x, y)).T:
            print "point(%e, %e)" % (xx, yy)


    if 0:
        clf()
        scatter(theta * to_deg * np.cos(phi),
                theta * to_deg * np.sin(phi), color="y")
        scatter(theta2 * to_deg * np.cos(phi),
                theta2 * to_deg * np.sin(phi), color="r")

        
        clf()
        to_deg = 180./np.pi
        scatter(x1, y1, color="y")
        scatter(x4, y4, color="r")


    if 0:
        #somehow writing directly back gives segfault white scamping.
       
        d[XKEY] = x4 #+ header["CRPIX1"]
        d[YKEY] = y4 #+ header["CRPIX2"]
        d[YKEY][d[YKEY] < 1] = 1.

        f.writeto("test_update1.cat", clobber=True,
                  output_verify="ignore")

    #f = pyfits.open("test.cat")
    #d = f[2].data
    x4, y4 = convert_xy(header, x, y)
    print type(x4)
    print type(d[XKEY])

    # writing directly back without reopening somehow give segfault error in scamp.
    f = pyfits.open(cat_name)
    d  = f[2].data
    d[XKEY][:] = x4 #+ header["CRPIX1"]
    d[YKEY][:] = y4 #+ header["CRPIX2"]

    if 0:
        fffout = open("test.reg", "w")
        fffout.writelines(["point(%e, %e)\n" % (xx, yy) for xx, yy in np.array((x4, y4)).T])
        fffout.close()

    basename, ext = os.path.splitext(os.path.basename(cat_name))
    outcatname = os.path.join(tmpdir, basename + "_flattened.cat")
    f.writeto(outcatname, clobber=True,
              output_verify="ignore")

    if 0:
        for xx, yy in np.array((d[XKEY], d[YKEY])).T:
            print "point(%e, %e)" % (xx, yy)

    if 1:
        from astropy.io import fits
        import numpy as np
        NX, NY = header["NAXIS1"], header["NAXIS2"]
        dx, dy = 100, 100
        iy, ix = np.meshgrid(np.linspace(1, NY, dy),
                             np.linspace(1, NX, dx))

        col1 = fits.Column(name='X', format='E', array=ix.flat)
        col2 = fits.Column(name='Y', format='E', array=iy.flat)
        
        cols = fits.ColDefs([col1, col2])
        tbhdu = fits.new_table(cols)


        grid_catname = os.path.join(tmpdir, basename + "_grid.cat")
        tbhdu.writeto(grid_catname, clobber=True)

        

        ix4, iy4 = convert_xy(header, np.ravel(ix), np.ravel(iy))
        col1 = fits.Column(name='X', format='E', array=ix4)
        col2 = fits.Column(name='Y', format='E', array=iy4)
        
        cols = fits.ColDefs([col1, col2])
        tbhdu = fits.new_table(cols)

        grid_catname_flattened = os.path.join(tmpdir, basename + "_grid_flattened.cat")
        tbhdu.writeto(grid_catname_flattened, clobber=True)

    return outcatname, grid_catname, grid_catname_flattened, header
    #d[YKEY][d[YKEY] < 1] = 1.

    #f2 = pyfits.open("test_update.cat")



if 0:
    f = pyfits.open("kmtc.20150329.007590.ne.fits")
    f[0].header["CRPIX1"]  = f[0].header["CRPIX1"] - 110
    f[0].header["CRPIX2"]  = f[0].header["CRPIX2"]
    f.writeto("test1.fits", clobber=True)

if 0:
    f = pyfits.open("kmtc.20150329.007590.ne.fits")
    f[0].header["CTYPE1"]  = 'RA---TAN'
    f[0].header["CTYPE2"]  = 'DEC--TAN'
    for pv in ["PV2_1", "PV2_2", "PV2_3"]:
        del f[0].header[pv]
    f.writeto("test2.fits")


import astropy.io.fits as pyfits
import numpy as np

def undistort_catalog2(cat_name, tmpdir):

    f = pyfits.open(cat_name)
    d  = f[2].data
    h  = f[2].data
    XKEY, YKEY = "X_IMAGE", "Y_IMAGE"

    cards = [pyfits.Card.fromstring(s) for s in f[1].data[0][0]]
    header = pyfits.Header(cards)

    #x, y = d["XWIN_IMAGE"][::100], d["YWIN_IMAGE"][::100]
    x, y = d[XKEY], d[YKEY]

    x1 = x - header["CRPIX1"]
    y1 = y - header["CRPIX2"]

    mat = np.matrix([[header["CD1_1"], header["CD1_2"]],
                     [header["CD2_1"], header["CD2_2"]]])
    xy2 = mat * (x1, y1)
    x2, y2 = np.array(xy2)
    # y2 = mat[1] * (x1, y1)
    # y2 = header["CD2_1"] * x1 + header["CD2_2"] * y1

    #x2 = np.array([1, 5, 3])/10.
    #y2 = np.array([3, 5, 3])/10.
    if 0:
        clf()
        scatter(x2, y2)

    phi = np.arctan2(y2, x2)
    theta_ = (x2**2 + y2**2)**.5 # in degree
    theta = theta_ * np.pi / 180. # to radian


    theta2 = theta - 35.*theta**3


    to_deg = 180./np.pi
    x3 = theta2 * to_deg * np.cos(phi)
    y3 = theta2 * to_deg * np.sin(phi)

    xy4 = mat.I * (x3, y3)
    x4, y4 = np.array(xy4)


    if 0:
        clf()
        scatter(theta * to_deg * np.cos(phi),
                theta * to_deg * np.sin(phi), color="y")
        scatter(theta2 * to_deg * np.cos(phi),
                theta2 * to_deg * np.sin(phi), color="r")


    clf()
    to_deg = 180./np.pi
    scatter(x1, y1, color="y")
    scatter(x4, y4, color="r")


    if 0:
        #somehow writing directly back gives segfault white scamping.
        d[XKEY] = x4 + header["CRPIX1"]
        d[YKEY] = y4 + header["CRPIX2"]
        d[YKEY][d[YKEY] < 1] = 1.

        f.writeto("test_update1.cat", clobber=True,
                  output_verify="ignore")

    f = pyfits.open("test.cat")
    d = f[2].data
    d[XKEY] = x4 + header["CRPIX1"]
    d[YKEY] = y4 + header["CRPIX2"]
    d[YKEY][d[YKEY] < 1] = 1.

    f.writeto("test_update.cat", clobber=True,
              output_verify="ignore")
    #f2 = pyfits.open("test_update.cat")


def pv2sip(pv_headerfile, naxis1, naxis2, tmpdir):
    pv2sip_name = "/home/jjlee/kmtnet/astrometry.net/util/wcs-pv2sip"
    basename, ext = os.path.splitext(os.path.basename(pv_headerfile))
    sip_headerfile = os.path.join(tmpdir, basename + ".sip_head")
    args = [pv2sip_name, "-s",
            "-W", str(naxis1),
            "-H", str(naxis2),
            pv_headerfile,
            sip_headerfile,
            ]
    print args
    import subprocess
    subprocess.call(args)

    return sip_headerfile

    #pv2sip_name -s -o 5 N2784-5.Q0.V.150303_0414.C.009568.091843N2208.0060_tan_flattened.head test.head -W 2049 -H 2059


def get_true_sip(sip_headerfile, xyls, xyls_flattened, tmpdir):
    xy2rd_name = "/home/jjlee/kmtnet/astrometry.net/util/wcs-xy2rd"
    fit_wcs_name = "/home/jjlee/kmtnet/astrometry.net/util/fit-wcs"
    basename, ext = os.path.splitext(os.path.basename(xyls))
    rdls = os.path.join(tmpdir, basename + ".rdls")
    args = [xy2rd_name, 
            "-w", sip_headerfile,
            "-i", xyls_flattened,
            "-o", rdls,
            ]
    print args
    import subprocess
    subprocess.call(args)

    sip_header_true = os.path.join(tmpdir, basename + ".sip_true_header")
    args = [fit_wcs_name, 
            "-s", "4",
            "-x", xyls,
            "-r", rdls,
            "-o", sip_header_true,
            ]
    print args
    import subprocess
    subprocess.call(args)

    return sip_header_true


if __name__ == "__main__":
    import os
    tmpdir = "tmp_update_wcs_kmtc.20150329.007590.ne.fits_qBj9ky"
    undistort_catalog(os.path.join(tmpdir, "kmtc.20150329.007590.ne.cat"),
                      tmpdir)

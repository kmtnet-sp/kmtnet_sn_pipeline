import numpy as np
import astropy.io.fits as pyfits

def get_dist(src, ref):
    f = pyfits.open(src)

    xw1 = np.median(f[2].data["X_WORLD"])
    yw1 = np.median(f[2].data["Y_WORLD"])

    fc = pyfits.open(ref)
    xw2 = np.median(fc[-1].data["X_WORLD"])
    yw2 = np.median(fc[-1].data["Y_WORLD"])

    dx = (xw1 - xw2) * np.cos(0.5*(yw1 + yw2)/180.*np.pi)
    dy = yw1 - yw2

    d = (dx**2 + dy**2)**.5
    dist_in_arcmin = d*60

    return dist_in_arcmin


if __name__ == "__main__":
    src = "./tmp_update_wcs_kmtc.20160629.005997.ne.fits_bVbucg/kmtc.20160629.005997.ne_tan_flattened.cat"
    ref = "kmtc.20160629.005997.ne.ref.cat"

    d = get_dist(src, ref) # distance in arcmin

    print d


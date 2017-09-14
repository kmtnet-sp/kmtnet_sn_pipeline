import numpy as np
import astropy.io.fits as pyfits

from astropy.coordinates import spherical_to_cartesian, cartesian_to_spherical
from astropy.coordinates import SkyCoord


def get_median_lonlat(lon, lat):
    "lon, lat in degrees"
    x, y, z = spherical_to_cartesian(1, (lat / 180. * np.pi), (lon / 180. * np.pi))
    # print(np.median(x))                                                                          
    # print(np.median(y))                                                                          
    # print(np.median(z))                                                                          

    r, lat, lon = cartesian_to_spherical(np.median(x), np.median(y), np.median(z))
    return lon, lat


def get_dist(src, ref):
    f = pyfits.open(src)

    lon1, lat1 = get_median_lonlat(f[2].data["X_WORLD"], f[2].data["Y_WORLD"])

    fc = pyfits.open(ref)

    lon2, lat2 = get_median_lonlat(fc[-1].data["X_WORLD"], fc[-1].data["Y_WORLD"])

    c1 = SkyCoord(lon1, lat1)
    c2 = SkyCoord(lon2, lat2)

    return c1.separation(c2).arcmin


    # dx = (xw1 - xw2) * np.cos(0.5*(yw1 + yw2)/180.*np.pi)
    # dy = yw1 - yw2

    # d = (dx**2 + dy**2)**.5
    # dist_in_arcmin = d*60

    # return dist_in_arcmin


if __name__ == "__main__":
    src = "./tmp_update_wcs_kmtc.20160629.005997.ne.fits_bVbucg/kmtc.20160629.005997.ne_tan_flattened.cat"
    ref = "kmtc.20160629.005997.ne.ref.cat"

    d = get_dist(src, ref) # distance in arcmin

    print d



import astropy.io.fits as pyfits
import os
import numpy as np

# chip_id, ext numbers, crpix
# extension numbers : index starts from 0 in python
# CRPIX1, CRPIX2 : these are just rough values.
chip_info = [("ne", (1, 9), (9826, -287)),
             ("nw", (9, 17), (164, -185)),
             ("se", (17, 25), (9761, 9891)),
             ("sw", (25, 33), (178, 9891))]


def combine_kmtnet(fn):

    fn_name, fn_ext = os.path.splitext(os.path.basename(fn))
    f = pyfits.open(fn)

    import astropy.units as u
    from astropy.coordinates import ICRS
    f[0].verify("fix")

    c = ICRS(f[0].header["RA"], f[0].header["DEC"],
             unit=(u.hourangle, u.degree))

    for chip_id, (ext1, ext2), (crpix1, crpix2) in chip_info:

        d_list = []
        for f1 in f[ext1: ext2]:
            d_list.append(f1.data[:,:1152]) # do not use overscan region

        dd = np.hstack(d_list)

        header = f[0].header.copy()
        header.extend(f[1].header)


        # modify headers
        header["CRVAL1"] = c.ra.degree
        header["CRVAL2"] = c.dec.degree


        header["CRPIX1"] = crpix1
        header["CRPIX2"] = crpix2

        header["CD1_1"] = -abs(header["CD1_1"])

        if 1:
            header["CTYPE1"]  = 'RA---ZPN'
            header["CTYPE2"]  = 'DEC--ZPN'


            header["PV2_1"]   = 1.
            header["PV2_2"]   = 0.
            header["PV2_3"]   = 35

            #header["PROJP1"]   = 1.
            #header["PROJP3"]   = 35
        elif 0:
            header["CTYPE1"]  = 'RA---TAN'
            header["CTYPE2"]  = 'DEC--TAN'
            header["PV1_0"]   = 0
            header["PV1_1"]   = 1
            header["PV1_11"]   = -0.009
            header["PV2_0"]   = 0
            header["PV2_1"]   = 1
            header["PV2_11"]   = -0.009
        elif 0:
            header["CTYPE1"]  = 'RA---TAN'
            header["CTYPE2"]  = 'DEC--TAN'
            header["PV1_0"]   = 0
            header["PV1_1"]   = 1
            header["PV1_11"]   = -0.007
            #header["PV1_7"]   = -0.012
            header["PV2_0"]   = 0
            header["PV2_1"]   = 1
            #header["PV2_7"]   = -0.012
            header["PV2_11"]   = -0.007
        else:
            header["CTYPE1"]  = 'RA---TAN'
            header["CTYPE2"]  = 'DEC--TAN'


        # delete unnecessary keys
        del header["CDELT1"]
        del header["CDELT2"]
        del header["DATASEC"]
        del header["LTV1"]
        del header["LTV2"]

        # replace key names
        for k in "RA DEC ST".split():
            header["KSP_%s" % k] = header.pop(k)

        hdu = pyfits.PrimaryHDU(data=dd, header=header)
        hdu.verify("fix")

        fout = os.path.extsep.join([fn_name, chip_id]) + fn_ext
        hdu.writeto(fout, output_verify="fix", clobber=True)


def test():
    fn = "../kmtc.20150211.003581.fits"
    combine_kmtnet(fn)


if __name__ == "__main__":
    import sys
    assert len(sys.argv) == 2

    fn = sys.argv[1]
    combine_kmtnet(fn)

import astropy.io.fits as pyfits
from astropy.wcs import WCS

def get_center(infile):
    f = pyfits.open(infile)
    if f[0].data is None:
        hdu = f[1]
    else:
        hdu = f[0]

    wcs = WCS(hdu.header)
    cx, cy = hdu.header["NAXIS1"] *.5, hdu.header["NAXIS2"] *.5
    radec_ = wcs.all_pix2world([(cx, cy)], 0)

    ra, dec = radec_[0]
    return ra, dec

def main():
    import argparse

    parser = argparse.ArgumentParser(description='get center.')
    parser.add_argument('infile', type=str, help='input file')

    arg = parser.parse_args()

    #print args.debug
    #print args.ref_name, args.tgt_name
    # delete_temp = not args.debug

    #print delete_temp

    ra, dec = get_center(arg.infile)
    print ra, dec



if __name__ == "__main__":

    main()


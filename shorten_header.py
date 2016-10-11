import astropy.io.fits as pyfits
import re

def shorten(inname, outname):
    f=pyfits.open(inname)
    p = re.compile(r"FILE\d+")
    for k in f[0].header.keys():
        if p.match(k): 
            del f[0].header[k]

    f.writeto(outname, clobber=True)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='shorten header by removing FILE- keywords')
    parser.add_argument('inname', type=str, help='input file name')
    parser.add_argument('outname', type=str, help='output name')


    args = parser.parse_args()

    shorten(args.inname, args.outname)


if __name__ == "__main__":
    main()

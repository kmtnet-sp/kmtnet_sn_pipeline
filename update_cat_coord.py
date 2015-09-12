from ksppy.phot import update_cat_coord


def main():
    import argparse

    parser = argparse.ArgumentParser(description='update wcs.')
    parser.add_argument('cat_name', type=str, help='input file name')
    parser.add_argument('fits_name', type=str, help='input nh.fits name')
    parser.add_argument('outcat_name', type=str, help='output cat name')


    args = parser.parse_args()

    update_cat_coord(args.cat_name, args.fits_name, args.outcat_name)


if __name__ == "__main__":
    main()

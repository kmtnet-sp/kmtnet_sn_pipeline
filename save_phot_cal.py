from ksppy.phot import save_phot


def main():
    import argparse

    parser = argparse.ArgumentParser(description='save-phot-cal.')
    parser.add_argument('fits_name', type=str, help='input nh.fits name')
    parser.add_argument('band', type=str, help='filter band (B, V, g, r, i)')

    parser.add_argument('phot_file', dest='phot_file',
                        default=None,
                        help='output file')

    args = parser.parse_args()

    save_phot(args.fits_name, args.band, phot_file=args.phot_file)


if __name__ == "__main__":
    main()

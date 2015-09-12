from ksppy.phot import do_phot, save_magzp

def main():
    import argparse

    parser = argparse.ArgumentParser(description='update wcs.')
    parser.add_argument('cat_name', type=str, help='input file name')
    parser.add_argument('fits_name', type=str, help='input nh.fits name')
    parser.add_argument('band', type=str, help='filter band (B, V, g, r, i)')
    parser.add_argument('magzp_name', type=str, help='output MAGZP name')

    parser.add_argument('--phot-dir', dest='phot_dir', action='store_const',
                        const=True, default=".",
                        help='directory where apass files will be located')

    parser.add_argument('--fig-dir', dest='fig_dir', action='store_const',
                        const=True, default=".",
                        help='directory where output figures will be located')


    args = parser.parse_args()

    r = do_phot(args.cat_name, args.fits_name, args.band, 
                args.phot_dir, args.fig_dir)

    save_magzp(r, args.magzp_name)


if __name__ == "__main__":
    main()

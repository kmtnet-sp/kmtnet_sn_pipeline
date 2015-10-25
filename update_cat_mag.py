from ksppy.phot import update_cat_mag


def main():
    import argparse

    parser = argparse.ArgumentParser(description='update MAG_AUTO using the given magzpt information')
    parser.add_argument('cat_name', type=str, help='input file name')
    parser.add_argument('magzpt_name', type=str, help='input magzpt name')
    parser.add_argument('outcat_name', type=str, help='output cat name')


    args = parser.parse_args()

    update_cat_mag(args.cat_name, args.magzpt_name, args.outcat_name)


if __name__ == "__main__":
    main()

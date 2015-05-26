"""
make_diff_image.py src_name ref_name out_name

Make a difference image , given source image and reference image.

1) SExtractore is run on the src_image to detect sources.
2) SCAMP is run with the source catalog from previous run
   to do absolute astrometry. Only header is updated. No modification
   to the image is done. 2MASS catalog is used for matching.
3) wcsremap is run to remap the reference image to the
   (astrometrically correct) source image.
4) hotpants is run to make a difference image between the two images.

"""

from ksppy.hotpants import tempfile, run_wcsremap, run_hotpants

TMP_PREFIX = "tmp_make_diff_image_"

def make_diff_image(src_name, ref_name, out_name, delete_temp=True):
    try:
        tmpdir = tempfile.mkdtemp(dir=".", prefix=TMP_PREFIX+src_name+"_")
        print tmpdir

        #catname = run_sex(src_name, tmpdir=tmpdir)
        #catname = "tmp/uwife040_FeII_S0_1v0_x_starsub.cat"

        #headername = run_scamp(catname, tmpdir=tmpdir)
        #headername = "tmp/uwife040_FeII_S0_1v0_x_starsub.head"

        #src_templatename = update_header(src_name, headername,
        # outdir=tmpdir, prefix="nh.fits")

        #src_templatename = "tmp/uwife040_FeII_S0_1v0_x_starsub.nh.fits"

        remaped_ref = run_wcsremap(ref_name, src_name, outdir=tmpdir)
        #remaped_ref = "tmp/uwife040_H_S0_1v0_x_starsub.ref.remap.fits"

        run_hotpants(src_name,
                     templatename=remaped_ref,
                     outname=out_name)

    finally:
        if delete_temp:
            import shutil
            shutil.rmtree(tmpdir)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='make diff images.')
    parser.add_argument('src_name', type=str, help='input file name')
    parser.add_argument('ref_name', type=str, help='reference image')
    parser.add_argument('out_name', type=str, help='out name')
    parser.add_argument('--debug', dest='debug', action='store_const',
                        const=True, default=False,
                        help='do not delete temp files')

    args = parser.parse_args()

    #print args.debug
    #print args.ref_name, args.tgt_name
    delete_temp = not args.debug

    if 0: # for test
        src_name = "uwife040_FeII_S0_1v0_x_starsub.fits"
        ref_name = "uwife040_H_S0_1v0_x_starsub.ref.fits"
        out_name = "starsub.fits"

    make_diff_image(args.src_name, args.ref_name, args.out_name,
                    delete_temp=delete_temp)

    #make_ref_image(ref_name, out_name)

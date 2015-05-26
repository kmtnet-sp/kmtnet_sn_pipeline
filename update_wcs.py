from ksppy.hotpants import (tempfile, run_sex, run_scamp, update_header,
                            run_swarp)
TMP_PREFIX = "tmp_update_wcs_"

def update_wcs(src_name, delete_temp=False):
    try:
        tmpdir = tempfile.mkdtemp(dir=".", prefix=TMP_PREFIX+src_name+"_")
        print tmpdir

        #src_name0, ext0 = os.path.splitext(src_name)
        if src_name.endswith(".fz"):
            import os
            basename = os.path.basename(src_name.replace(".fz", ""))
            src_name0 = os.path.join(tmpdir,basename)
            os.system("funpack -O %s %s" % (src_name0, src_name))
        else:
            src_name0 = src_name

        resamp_name = run_swarp(src_name0, tmpdir=tmpdir)
        catname = run_sex(resamp_name, tmpdir=tmpdir)
        #catname = "tmp/uwife040_FeII_S0_1v0_x_starsub.cat"

        headername = run_scamp(catname, tmpdir=tmpdir)
        #headername = "tmp/uwife040_FeII_S0_1v0_x_starsub.head"

        #src_name = "kmtc.20150211.003540.ne.fits"
        #headername = "tmpD5iOJ_/test.ne.head"
        src_templatename = update_header(resamp_name, headername,
                                         outdir=".", prefix="nh.fits", extnum=0)

        print src_templatename

    finally:
        if delete_temp:
            import shutil
            shutil.rmtree(tmpdir)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='update wcs.')
    parser.add_argument('src_name', type=str, help='input file name')
    #parser.add_argument('tgt_name', type=str, help='target file name')
    parser.add_argument('--debug', dest='debug', action='store_const',
                        const=True, default=False,
                        help='do not delete temp files')

    args = parser.parse_args()

    #print args.debug
    #print args.ref_name, args.tgt_name
    delete_temp = not args.debug

    print delete_temp

    update_wcs(args.src_name, delete_temp=delete_temp)

    #make_ref_image(ref_name, out_name)

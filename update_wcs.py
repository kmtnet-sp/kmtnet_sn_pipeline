from make_diff_image import (tempfile, run_sex, run_scamp, update_header,
                             run_swarp)

def update_wcs(src_name):
    tmpdir = tempfile.mkdtemp(dir=".")
    print tmpdir

    resamp_name = run_swarp(src_name, tmpdir=tmpdir)
    catname = run_sex(resamp_name, tmpdir=tmpdir)
    #catname = "tmp/uwife040_FeII_S0_1v0_x_starsub.cat"

    headername = run_scamp(catname, tmpdir=tmpdir)
    #headername = "tmp/uwife040_FeII_S0_1v0_x_starsub.head"

    #src_name = "kmtc.20150211.003540.ne.fits"
    #headername = "tmpD5iOJ_/test.ne.head"
    src_templatename = update_header(resamp_name, headername,
                                     outdir=".", prefix="nh.fits", extnum=0)

    print src_templatename



if __name__ == "__main__":
    import sys

    assert len(sys.argv) == 2

    src_name = sys.argv[1]


    update_wcs(src_name)

    #make_ref_image(ref_name, out_name)

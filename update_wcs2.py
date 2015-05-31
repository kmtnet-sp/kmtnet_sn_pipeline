from ksppy.hotpants import (tempfile, run_sex, run_scamp, update_header,
                            update_header_sip,
                            run_swarp)
TMP_PREFIX = "tmp_update_wcs_"

def modify_header(src_name, tmpdir):
    import os
    import astropy.io.fits as pyfits

    basename, ext = os.path.splitext(os.path.basename(src_name))
    outname = os.path.join(tmpdir, basename + "_tan.fits")

    f = pyfits.open(src_name)
    f[0].header["CTYPE1"]  = 'RA---TAN'
    f[0].header["CTYPE2"]  = 'DEC--TAN'
    for pv in ["PV2_1", "PV2_2", "PV2_3"]:
        del f[0].header[pv]
    f.writeto(outname, clobber=True, output_verify="fix")
    return outname

def update_wcs(src_name, delete_temp=False):
    try:
        tmpdir = tempfile.mkdtemp(dir=".", prefix=TMP_PREFIX+src_name+"_")
        print tmpdir

        import os

        #src_name0, ext0 = os.path.splitext(src_name)
        if src_name.endswith(".fz"):
            basename = os.path.basename(src_name[:-3]) #.replace(".fz", ""))
            src_name0 = os.path.join(tmpdir,basename)
            os.system("funpack -O %s %s" % (src_name0, src_name))
        else:
            src_name0 = src_name

        src_basename = os.path.basename(src_name0[:-4])
        
        src_name1 = modify_header(src_name0, tmpdir)
        # without header modification, scamp never finishes.

        catname = run_sex(src_name1, tmpdir=tmpdir, out_dir=".")
        #catname = "tmp/uwife040_FeII_S0_1v0_x_starsub.cat"

        from undistort_catalog import undistort_catalog

        flattened_catname, xyls, xyls_flattened, header = \
            undistort_catalog(catname, tmpdir)

        headername = run_scamp(flattened_catname, tmpdir=tmpdir)
        from ksppy.hotpants import zip_output
        #os. basename
        zipname = zip_output(src_basename, tmpdir)


        from undistort_catalog import pv2sip, get_true_sip
        sip_headername_intermediate = pv2sip(headername, 
                                             header["NAXIS1"], header["NAXIS2"],
                                             tmpdir)

        sip_headername = get_true_sip(sip_headername_intermediate, 
                                      xyls,
                                      xyls_flattened,
                                      tmpdir)

        src_templatename = update_header_sip(src_name0, sip_headername,
                                             outdir=".", prefix="nh.fits", 
                                             extnum=0)

    finally:
        if delete_temp:
            import shutil
            shutil.rmtree(tmpdir)


def main():
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



def main2():
    import os

    tmpdir = "tmp_update_wcs_N2784-5.Q0.V.150303_0414.C.009568.091843N2208.0060.fits_MNKJan"

    basename = "N2784-5.Q0.V.150303_0414.C.009568.091843N2208.0060"
    src_name0 = "N2784-5.Q0.V.150303_0414.C.009568.091843N2208.0060.fits"

    if 0:
        src_name1 = modify_header(src_name0, tmpdir)
        # without header modification, scamp never finishes.
    else:
        src_name1 = basename + "_tan.fits"

    if 0:
        catname = run_sex(src_name1, tmpdir=tmpdir, out_dir=".")
        #catname = "tmp/uwife040_FeII_S0_1v0_x_starsub.cat"
    else:
        catname = basename + "_tan.cat"

    if 1:
        from undistort_catalog import undistort_catalog

        flattened_catname, xyls, xyls_flattened, header = \
            undistort_catalog(catname, tmpdir)


    if 0:
        headername = run_scamp(flattened_catname, tmpdir=tmpdir)
    else:
        headername = os.path.join(tmpdir, basename+"_tan_flattened.head")

    if 1:

        from ksppy.hotpants import zip_output
        #os. basename
        zipname = zip_output(basename, tmpdir)


        from undistort_catalog import pv2sip, get_true_sip
        sip_headername_intermediate = pv2sip(headername, 
                                             header["NAXIS1"], header["NAXIS2"],
                                             tmpdir)

        sip_headername = get_true_sip(sip_headername_intermediate, 
                                      xyls,
                                      xyls_flattened,
                                      tmpdir)

        src_templatename = update_header_sip(src_name0, sip_headername,
                                             outdir=".", prefix="nh.fits", 
                                             extnum=0)


if __name__ == "__main__":
    main()

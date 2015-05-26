
from ksppy.hotpants import tempfile, run_sex_diff


import astropy
import astropy.io.fits as pyfits
import numpy as np
import os

def update_cat_region(in_name, cat_name):
    f=pyfits.open(in_name)

    tbl = f[2].data

    msk0 = tbl["ELONGATION"] > 3
    msk1 = (tbl["FWHM_IMAGE"] < 2) | (tbl["FWHM_IMAGE"] > 6.5)
    msk2 = (tbl["CLASS_STAR"] < 0.4)

    thresh = np.abs(tbl["FLUX_MAX"])*0.1
    num_pos = (tbl["VIGNET"] > thresh[:,np.newaxis,np.newaxis]).sum(axis=1).sum(axis=1)
    num_neg = (tbl["VIGNET"] < -thresh[:,np.newaxis,np.newaxis]).sum(axis=1).sum(axis=1)

    neg_fraction = num_neg*1./num_pos
    msk3 = neg_fraction > 0.1

    msk = msk0 | msk1 | msk2 | msk3

    col = pyfits.Column(name="KSP_SOURCE_CLASS", format="32X",
                        array=msk)

    f[2].columns.add_col(col)
    f[2] = pyfits.BinTableHDU.from_columns(f[2].columns)

    f[2].header["KSP_FWHM"] = np.median(f[2].data["FWHM_WORLD"]) * 3600.

    f.writeto(cat_name, clobber=True)

def make_region(cat_name, region_name):
    d=pyfits.open(cat_name)

    tbl = d[2].data

    msk = tbl["KSP_SOURCE_CLASS"].sum(axis=1).astype(bool)

    fmt = "point(%f,%f) # point=cross color=green text={%04d}\n"
    bad_points = [fmt % (row["X_IMAGE"], row["Y_IMAGE"], row["NUMBER"]) for row in tbl[msk]]
    fmt = "point(%f,%f) # point=circle color=red text={%04d}\n"
    good_points = [fmt % (row["X_IMAGE"], row["Y_IMAGE"], row["NUMBER"]) for row in tbl[~msk]]

    fout = open(region_name,"w")
    fout.write("image\n")
    fout.writelines(bad_points)
    fout.writelines(good_points)
    fout.close()


TMP_PREFIX = "tmp_find_sources_"

def find_sources(src_name, delete_temp=True):
    try:
        tmpdir = tempfile.mkdtemp(dir=".", prefix=TMP_PREFIX+src_name+"_")
        print tmpdir

        catname = run_sex_diff(src_name, tmpdir=tmpdir)

        catname2 = os.path.basename(catname)

        #import shutil
        #shutil.move(catname, catname2)

        update_cat_region(catname, catname2)        

        root, ext = os.path.splitext(catname2)
        prefix = "reg"
        outname = os.path.extsep.join([root, prefix])

        make_region(catname2, outname)

    finally:
        if delete_temp:
            import shutil
            shutil.rmtree(tmpdir)
    


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='update wcs.')
    parser.add_argument('src_name', type=str, help='input file name')
    parser.add_argument('--debug', dest='debug', action='store_const',
                        const=True, default=False,
                        help='do not delete temp files')

    args = parser.parse_args()
    delete_temp = not args.debug

    find_sources(args.src_name, delete_temp=delete_temp)

    #make_ref_image(ref_name, out_name)

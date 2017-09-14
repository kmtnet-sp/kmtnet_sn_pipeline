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

import subprocess
import tempfile
import os
import numpy as np

# PACKAGE_DIR = os.environ.get("KSPPY_PACKAGES_DIR", "/packages")

# my_env = os.environ.copy()
# my_env["LD_LIBRARY_PATH"] =":".join([os.path.join(PACKAGE_DIR,
#                                                   "astromatic/usr/lib"),
#                                      os.path.join(PACKAGE_DIR,
#                                                   "astromatic/usr/lib/atlas")])


# executables = dict(sex=os.path.join(PACKAGE_DIR, "astromatic/usr/bin/sex"),
#                    #swarp="/data/packages/astromatic/usr/bin/swarp",
#                    #wcsremap="wcsremap",
#                    #hotpants="hotpants",
#                    #sip2pv="sip2pv",
#                    wcsremap=os.path.join(PACKAGE_DIR, "wcsremap/wcsremap"),
#                    hotpants=os.path.join(PACKAGE_DIR, "hotpants/hotpants"),
#                    sip2pv=os.path.join(PACKAGE_DIR, "sip/sip2pv"),
#                    scamp=os.path.join(PACKAGE_DIR, "astromatic/usr/bin/scamp"),
#                    psfex=os.path.join(PACKAGE_DIR, "astromatic/usr/bin/psfex"),
#                    swarp=os.path.join(PACKAGE_DIR, "astromatic/usr/bin/swarp"))

import exec_path
my_env = exec_path.get_env()
executables = exec_path.get_exec_path()

_ROOT = os.path.abspath(os.path.dirname(__file__))
def get_params_dir():
    return os.path.join(_ROOT, 'params')

params_dir = get_params_dir()

import contextlib

@contextlib.contextmanager
def temp_chdir(path):
    """
    Usage:
    >>> with temp_chdir(gitrepo_path):
    ...   subprocess.call('git status')
    """
    starting_directory = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(starting_directory)

def run_sex(filename, outname_root=None, tmpdir=".",
            params_dir=params_dir, out_dir=None):

    filename = os.path.abspath(filename)

    if outname_root is None:
        filename_base = os.path.basename(filename)
        outname_root, ext_name = os.path.splitext(filename_base)

    outname = os.path.extsep.join([outname_root, "cat"])
    if out_dir is not None:
        outname = os.path.abspath(os.path.join(out_dir, outname))

    args = [executables["sex"], filename]

    param_files = [("c", "default.sex"),
                   ("PARAMETERS_NAME", "default4psfex.param"),
                   ("FILTER_NAME", "default.conv"),
                   ("STARNNW_NAME", "default.nnw")]

    params_dir = os.path.abspath(params_dir)
    for par_name, par_file in param_files:
        a1 = "-%s" % par_name
        a2 = os.path.join(params_dir, par_file)
        args.extend([a1, a2])

    args.extend(["-CATALOG_NAME", outname])

    with temp_chdir(tmpdir):
        subprocess.call(args, env=my_env)

    return os.path.join(tmpdir, outname)


def run_sex_diff(filename, outname_root=None, tmpdir=".",
                 params_dir=params_dir):

    filename = os.path.abspath(filename)

    if outname_root is None:
        filename_base = os.path.basename(filename)
        outname_root, ext_name = os.path.splitext(filename_base)

    outname = os.path.extsep.join([outname_root, "cat"])

    args = [executables["sex"], filename]

    param_files = [("c", "default_diff.sex"),
                   ("PARAMETERS_NAME", "default4psfex_diff.param"),
                   ("FILTER_NAME", "default.conv"),
                   ("STARNNW_NAME", "default.nnw")]

    params_dir = os.path.abspath(params_dir)
    for par_name, par_file in param_files:
        a1 = "-%s" % par_name
        a2 = os.path.join(params_dir, par_file)
        args.extend([a1, a2])

    args.extend(["-CATALOG_NAME", outname])

    with temp_chdir(tmpdir):
        subprocess.call(args, env=my_env)

    return os.path.join(tmpdir, outname)


def run_swarp(filename, outname_root=None, tmpdir=".",
              params_dir=params_dir):

    filename = os.path.abspath(filename)

    if outname_root is None:
        filename_base = os.path.basename(filename)
        outname_root, ext_name = os.path.splitext(filename_base)

    outname = os.path.extsep.join([outname_root, "resamp", "fits"])

    args = [executables["swarp"], filename]

    # as we do not combine, output name is fixed to "resamp".
    param_files = [#("IMAGEOUT_NAME", outname),
                   ("COMBINE", "N"),
                   ("SUBTRACT_BACK", "Y")]

    params_dir = os.path.abspath(params_dir)
    for par_name, par_file in param_files:
        args.extend(["-%s" % par_name, par_file])

    with temp_chdir(tmpdir):
        subprocess.call(args, env=my_env)

    return os.path.join(tmpdir, outname)

def run_scamp(filename, tmpdir=".", catname=None,
              params_dir=params_dir):

    filename = os.path.abspath(filename)

    args = [executables["scamp"], filename]

    param_files = [("c", "default.scamp")]

    params_dir = os.path.abspath(params_dir)
    for par_name, par_file in param_files:
        a1 = "-%s" % par_name
        a2 = os.path.join(params_dir, par_file)
        args.extend([a1, a2])

    if catname is not None:
        args.extend(["-ASTREF_CATALOG", "FILE"])
        catname = os.path.abspath(catname)
        args.extend(["-ASTREFCAT_NAME", catname])

        print "catname", catname


    #args.extend(["-WRITE_XML", "N"])


    with temp_chdir(tmpdir):
        print args
        subprocess.call(args, env=my_env)

    outname_root, ext_name = os.path.splitext(filename)
    # scamp_zipname = os.path.extsep.join([outname_root+"_scamp", "zip"])

    # import zipfile, glob
    # with zipfile.ZipFile(scamp_zipname, "w") as myzip:
    #     with temp_chdir(tmpdir):
    #         for fn in sorted(glob.glob(os.path.join(tmpdir, "*.ps"))):
    #             myzip.write(fn)
    #         myzip.write("scamp.xml")

    return os.path.extsep.join([outname_root, "head"])

def zip_output(basename, tmpdir):
    #outname_root, ext_name = os.path.splitext(filename)
    zipname = os.path.extsep.join([basename+"_scamp", "zip"])

    import zipfile, glob
    with zipfile.ZipFile(zipname, "w") as myzip:
        with temp_chdir(tmpdir):
            for fn in sorted(glob.glob("*.svg")):
                myzip.write(fn)
            for fn in sorted(glob.glob("*.xml")):
                myzip.write(fn)

    return zipname

def update_header(inname, headername, outdir, prefix, extnum=0):
    import astropy.io.fits as pyfits
    import os

    root, ext = os.path.splitext(os.path.basename(inname))
    outname = os.path.join(outdir, os.path.extsep.join([root, prefix]))

    f = pyfits.open(inname)

    # f_weight = pyfits.open(os.path.splitext(inname)[0]+".weight.fits")
    # f[0].data[f_weight[0].data == 0] = np.nan

    header = f[extnum].header
    # for pv in ["PV2_1", "PV2_2", "PV2_3"]:
    #     del header[pv]

    for l in open(headername):
        k, v, c = tuple(pyfits.Card.fromstring(l))
        if k != "END":
            header.set(k, v, comment=c)

    #f[0].data[~np.isfinite(f[0].data)] = 0.
    f.writeto(outname, clobber=True, output_verify="fix")
    return outname


def update_header_sip(inname, headername, outdir, prefix, extnum=0):
    """
    update header for astrometry.net produced header file
    """
    import astropy.io.fits as pyfits
    import os

    root, ext = os.path.splitext(os.path.basename(inname))
    outname = os.path.join(outdir, os.path.extsep.join([root, prefix]))

    f = pyfits.open(inname)

    # f_weight = pyfits.open(os.path.splitext(inname)[0]+".weight.fits")
    # f[0].data[f_weight[0].data == 0] = np.nan

    header = f[extnum].header
    for pv in ["PV2_1", "PV2_2", "PV2_3"]:
        del header[pv]

    # for ctype in ["CTYPE1", "CTYPE2"]:
    #     if  header[ctype].endswith("-SIP"):
    #         header[ctype] = header[ctype][:-4]

    new_header = pyfits.open(headername)[0].header
    header.extend(new_header.cards, update=True)

    f.writeto(outname, clobber=True, output_verify="fix")
    return outname


def remove_tan_from_header(inname, outdir, extnum=0):
    """
    update header for astrometry.net produced header file
    """
    import astropy.io.fits as pyfits
    import os

    basename = os.path.basename(inname)
    outname = os.path.join(outdir, basename)

    f = pyfits.open(inname)
    header = f[extnum].header
    for ctype in ["CTYPE1", "CTYPE2"]:
        if  header[ctype].endswith("-SIP"):
            header[ctype] = header[ctype][:-4]

    f.writeto(outname, clobber=True, output_verify="fix")
    return outname


def run_sip2pv(sip_name, outname):


    if os.path.exists(outname):
        os.remove(outname)
    args = [executables["sip2pv"]]

    args.extend(["-i", sip_name])
    args.extend(["-o", outname])

    subprocess.call(args, env=my_env)
    return outname

def run_psfex(catname, tmpdir):


    # args = ["ldd", executables["psfex"]]

    # with temp_chdir(tmpdir):
    #     subprocess.call(args, env=my_env)

    args = [executables["psfex"]]

    args.extend(["-CHECKPLOT_DEV", "SVG"])
    args.extend(["-SAMPLE_AUTOSELECT", "N"])
    args.extend(["-PSF_SAMPLING", "0.8"])
    args.extend([catname])

    with temp_chdir(tmpdir):
        subprocess.call(args, env=my_env)

def run_wcsremap(srcname, templatename, outdir):


    args = [executables["wcsremap"]]

    outname_root, ext_name = os.path.splitext(os.path.basename(srcname))
    outname = os.path.join(outdir,
                           os.path.extsep.join([outname_root, "remap.fits"]))
    print outname
    args.extend(["-source", srcname])
    args.extend(["-template", templatename])
    args.extend(["-outIm", outname])

    subprocess.call(args, env=my_env)
    return outname


def run_hotpants(srcname, templatename, outname):


    args = [executables["hotpants"]]

    args.extend(["-inim", srcname])
    args.extend(["-tmplim", templatename])
    args.extend(["-outim", outname])

    args.extend(["-tl", "-100"])
    args.extend(["-il", "-100"])
    args.extend(["-nrx", "2"])
    args.extend(["-nry", "2"])

    args.extend(["-nsx", "15"])
    args.extend(["-nsy", "15"])
    args.extend("-ng  4 7 0.70 6 1.50 4 3.00 3 6.0".split())

    subprocess.call(args, env=my_env)
    return outname


def make_diff_image(src_name, ref_name, out_name):
    tmpdir = tempfile.mkdtemp(dir=".")
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


def make_ref_image(ref_name, out_name):
    tmpdir = tempfile.mkdtemp(dir=".")
    #tmpdir = "tmp"
    print tmpdir
    catname = run_sex(ref_name, tmpdir=tmpdir)
    #catname = "tmp/uwife040_FeII_S0_1v0_x_starsub.cat"
    run_scamp(catname, tmpdir=tmpdir)



if __name__ == "__main__":
    import sys

    assert len(sys.argv) == 4

    src_name = sys.argv[1]
    ref_name = sys.argv[2]
    out_name = sys.argv[3]

    if 0: # for test
        src_name = "uwife040_FeII_S0_1v0_x_starsub.fits"
        ref_name = "uwife040_H_S0_1v0_x_starsub.ref.fits"
        out_name = "starsub.fits"

    make_diff_image(src_name, ref_name, out_name)

    #make_ref_image(ref_name, out_name)

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

my_env = os.environ.copy()
my_env["LD_LIBRARY_PATH"]="/packages/astromatic/usr/lib"

executables = dict(sex="/packages/astromatic/usr/bin/sex",
                   #swarp="/data/packages/astromatic/usr/bin/swarp",
                   wcsremap="wcsremap",
                   scamp="/packages/astromatic/usr/bin/scamp",
                   hotpants="hotpants",
                   swarp="/packages/astromatic/usr/bin/swarp")

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
            params_dir=params_dir):

    filename = os.path.abspath(filename)

    if outname_root is None:
        filename_base = os.path.basename(filename)
        outname_root, ext_name = os.path.splitext(filename_base)

    outname = os.path.extsep.join([outname_root, "cat"])

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
        subprocess.call(args)

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
        subprocess.call(args)

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
                   ("SUBTRACT_BACK", "N")]

    params_dir = os.path.abspath(params_dir)
    for par_name, par_file in param_files:
        args.extend(["-%s" % par_name, par_file])

    with temp_chdir(tmpdir):
        subprocess.call(args)

    return os.path.join(tmpdir, outname)

def run_scamp(filename, tmpdir=".",
              params_dir=params_dir):

    filename = os.path.abspath(filename)

    args = [executables["scamp"], filename]

    param_files = [("c", "default.scamp")]

    params_dir = os.path.abspath(params_dir)
    for par_name, par_file in param_files:
        a1 = "-%s" % par_name
        a2 = os.path.join(params_dir, par_file)
        args.extend([a1, a2])

    #args.extend(["-WRITE_XML", "N"])

    with temp_chdir(tmpdir):
        print args
        subprocess.call(args, env=my_env)

    outname_root, ext_name = os.path.splitext(filename)
    return os.path.extsep.join([outname_root, "head"])

def update_header(inname, headername, outdir, prefix, extnum=0):
    import astropy.io.fits as pyfits

    root, ext = os.path.splitext(os.path.basename(inname))
    outname = os.path.join(outdir, os.path.extsep.join([root, prefix]))

    f = pyfits.open(inname)

    for l in open(headername):
        k, v, c = tuple(pyfits.Card.fromstring(l))
        if k != "END":
            f[extnum].header.set(k, v, comment=c)

    #f[0].data[~np.isfinite(f[0].data)] = 0.
    f.writeto(outname, clobber=True)
    return outname

def run_wcsremap(srcname, templatename, outdir):


    args = [executables["wcsremap"]]

    outname_root, ext_name = os.path.splitext(srcname)
    outname = os.path.join(outdir,
                           os.path.extsep.join([outname_root, "remap.fits"]))

    args.extend(["-source", srcname])
    args.extend(["-template", templatename])
    args.extend(["-outIm", outname])

    subprocess.call(args)
    return outname


def run_hotpants(srcname, templatename, outname):


    args = [executables["hotpants"]]

    args.extend(["-inim", srcname])
    args.extend(["-tmplim", templatename])
    args.extend(["-outim", outname])

    args.extend(["-tl", "-1000"])
    args.extend(["-il", "-1000"])

    subprocess.call(args)
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

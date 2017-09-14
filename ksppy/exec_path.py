import os

PACKAGE_DIR = os.environ.get("KSPPY_PACKAGES_DIR", "/packages")

def get_env():
    my_env = os.environ.copy()
    my_env["LD_LIBRARY_PATH"] =":".join([os.path.join(PACKAGE_DIR,
                                                      "astromatic/usr/lib"),
                                         os.path.join(PACKAGE_DIR,
                                                      "astromatic/usr/lib/atlas")])

def get_exec_path():
    executables = dict(sex=os.path.join(PACKAGE_DIR, "astromatic/usr/bin/sex"),
                       #swarp="/data/packages/astromatic/usr/bin/swarp",
                       #wcsremap="wcsremap",
                       #hotpants="hotpants",
                       #sip2pv="sip2pv",
                       wcsremap=os.path.join(PACKAGE_DIR, "wcsremap/wcsremap"),
                       hotpants=os.path.join(PACKAGE_DIR, "hotpants/hotpants"),
                       sip2pv=os.path.join(PACKAGE_DIR, "sip/sip2pv"),
                       scamp=os.path.join(PACKAGE_DIR, "astromatic/usr/bin/scamp"),
                       psfex=os.path.join(PACKAGE_DIR, "astromatic/usr/bin/psfex"),
                       swarp=os.path.join(PACKAGE_DIR, "astromatic/usr/bin/swarp"),
                       pv2sip=os.path.join(PACKAGE_DIR, "astrometry.net/util/wcs-pv2sip"),
                       xy2rd=os.path.join(PACKAGE_DIR, "astrometry.net/util/wcs-xy2rd"),
                       fit_wcs=os.path.join(PACKAGE_DIR, "astrometry.net/util/fit-wcs"))

    return executables


def check_exec_path():
    for k, v in get_exec_path().items():
        if os.path.exists(v):
            print "OK : ", k, v
        else:
            print "NOT FOUND : ", k, v


if __name__ == "__main__":
    check_exec_path()

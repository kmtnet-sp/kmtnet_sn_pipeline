import numpy as np
from astropy.io import fits

def get_ldac_head():
    "return dummy dummy header"

    s0 = "H4sICMXF+1cAA3JlZjAxLmNhdADtmVFzmkAUhftT7pvJtBrAoOQhDwhrwoyChbXRp8xW1ykdgRRwqv++u4CaRJDE2s50umd4Avab3T3LzLkXzxqOBgjgFkqE4QpmUbiI4iCBNIK+hT1IUhLOSTwvGwDQs/DImlTwNMYjcUw2MCcpgXTzRMspe9n6xPKggicxXrgKvtIYosWW7Ac0TPwoTEp5aIKRbVau993KYEJCQkJCQkJCQv+NeJz0LMe+hUbPsrHeG6DGs8dXgO9ZfmWXzqKxrbtTyN6Bi77rDNlDBANTN7DjDLxLPqA2P79TR/OzciJPLuPJHY3n8d4UIw9GyAXXeXgjT6mYn8x49njYYzCnz3leLW9kOGMbH6kXXN022c6PdFcfIszIxYAK3R3j8fnduc54VAN5Jty30MD0qnnF82IDaxfM6hmbLYTxGvwgPVrDe6SbuyN4VRy37J03zQ9PRyjzt9H36XIO95TMWX1lsIqvUT/8kNd33GHO4wdEZ7dOwex5psVxnHehSZ+g3bn8LZ6o34SEhISEhP6+vLr+M/7mJ8AuknefF/7yaM/4aH6W/kB+Vsy8mf0eXll+ljtt7Zrn3V0/O45+lvewD3hl+fmQN4uWq6CiLb5TTX+88CNzISAb/ncgJX6Ye0PX6UHrHX0eW7Yz2fMUSZJaUiHGG1ISAv2x8sNoXbtaYPHdRN6U5+eGZbhZPH5Zb+lJGkcBTWN/BskmSWlwlGfs866rN5tND9+95D0YHjzF0Xc6S9nK8n8WiyiGlO8DWfuv9tMY2xbOedtbr+bHh6xCP33DYjnP/aIPivOitNRut6t1NfVaUlX0Mdu/hyhmKX0WRfHcD0lKgU+yfG45j30eBU9ryTeKuvWC8dq8PqILGtNwRuHJX9NlDQ4MU37M8ziA2lL36qCmpDLewA8piZ9vYUCYOVVec55S8PbnpJifdAKP+5t9Hw0TGWfyVzmzv/n322y3NOWm21FvlG6nK7P1yif6q5zTX2Xn71n8YLytv+c4L+eu3z4ICQkJ/SP6BcXjxlPAIQAA"

    import base64
    ff0 = base64.b64decode(s0)
    import gzip, StringIO
    ff1 = gzip.GzipFile("ref0.cat", "r",
                       fileobj=StringIO.StringIO(ff0))
    f = fits.open(ff1)
    return f[1]

def convert_hdu_to_ldac(hdu):
    """
    Convert an hdu table to a fits_ldac table (format used by astromatic suite)
    
    Parameters
    ----------
    hdu: `astropy.io.fits.BinTableHDU` or `astropy.io.fits.TableHDU`
        HDUList to convert to fits_ldac HDUList
    
    Returns
    -------
    tbl1: `astropy.io.fits.BinTableHDU`
        Header info for fits table (LDAC_IMHEAD)
    tbl2: `astropy.io.fits.BinTableHDU`
        Data table (LDAC_OBJECTS)
    """
    # #tblhdr = np.array([c.image for c in hdu.header.cards if c[0]])
    # tblhdr = hdu.header.tostring('')
    # col1 = fits.Column(name='Field Header Card', array=[tblhdr], format='1680A')
    # cols = fits.ColDefs([col1])
    # tbl1 = fits.BinTableHDU.from_columns(cols)
    # tbl1.header['TDIM1'] = '(80, {0})'.format(len(hdu.header))
    # tbl1.header['EXTNAME'] = 'LDAC_IMHEAD'

    #tbl1 = fits.open("ref0.cat")[1]
    tbl1 = get_ldac_head()

    dcol = fits.ColDefs(hdu.data)
    tbl2 = fits.BinTableHDU.from_columns(dcol)
    tbl2.header['EXTNAME'] = 'LDAC_OBJECTS'
    return (tbl1, tbl2)


def load_cat(fname):
    xwl, ywl, xewl, yewl = [], [], [], []
    magl = []

    lall = open(fname).readlines()
    for l in lall[:]:

        if l.startswith("#GSC"): continue
        elif l[0] == "#": continue

        #print l.split("|")
        cl = int(l[172:174])
        if cl == 5:
            continue
        xw, yw, xew, yew = map(float, [l[33:][:10], l[43:][:10],
                                       l[54:][:5], l[60:][:5]])

        try:
            #print l[108:108+5]
            mag = float(l[92:92+5])
        except ValueError:
            mag = 99

        # print xw, yw, xew, yew
        xwl.append(xw)
        ywl.append(yw)
        xewl.append(xew)
        yewl.append(yew)
        magl.append(mag)

    # print xewl

    print "# of stars retrieved :", len(xwl)
    nn = len(xwl)

    #print np.array(xewl).dtype

    cor = 1./3600.  # arcsec to degree

    columns = [fits.Column(name='X_WORLD', format='E', array=np.array(xwl)),
               fits.Column(name='Y_WORLD', format='E', array=np.array(ywl)),
               fits.Column(name='ERRA_WORLD', format='E',
                           array=np.array(xewl)*cor),
               fits.Column(name='ERRB_WORLD', format='E',
                           array=np.array(yewl)*cor),
               fits.Column(name='MAG', format='E',
                           array=np.array(magl)),
               fits.Column(name='MAGERR', format='E',
                           array=np.zeros(nn, dtype=float)),
               fits.Column(name='OBSDATE', format='E',
                           array=np.zeros(nn, dtype=float)),
               ]

    print columns[4].array

    tbhdu = fits.BinTableHDU.from_columns(columns)

    return tbhdu

def fetch_catalog(ra, dec, radius, outname):
    "ra, dec in degree, radius in minute"

    cc = "%.7f%+.7f" % (ra, dec)

    fname = "table.out"

    import os
    cmd = "findgsc2.3 -c %s -r %.1f -m 999999 -T180 > %s" % (cc, radius, 
                                                            fname)
    r = os.system(cmd)

    print r

    tbhdu = load_cat(fname)
    tb1, tb2 = convert_hdu_to_ldac(tbhdu)
    hdu_list = [fits.PrimaryHDU(), tb1, tb2]

    fits.HDUList(hdu_list).writeto(outname, clobber=True)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='download catalog.')
    parser.add_argument('ra', type=float, help='RA in degree')
    parser.add_argument('dec', type=float, help='Dec in degree')
    parser.add_argument('radius', type=float, help='radius in arcminute')
    parser.add_argument('cat_name', type=str, help='cat file name')

    # parser.add_argument('--debug', dest='debug', action='store_const',
    #                     const=True, default=False,
    #                     help='do not delete temp files')

    arg = parser.parse_args()

    #print args.debug
    #print args.ref_name, args.tgt_name
    # delete_temp = not args.debug

    #print delete_temp

    fetch_catalog(arg.ra, arg.dec, arg.radius, arg.cat_name)

    #make_ref_image(ref_name, out_name)


if __name__ == "__main__":

    main()


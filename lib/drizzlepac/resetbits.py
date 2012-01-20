#!/usr/bin/env python

""" resetbits - A module to set the value of specified array pixels to zero

    This module allows a user to reset the pixel values of any integer array,
    such as the DQ array from an HST image, to zero.

    License:
        http://www.stsci.edu/resources/software_hardware/pyraf/LICENSE

    PARAMETERS
    ----------
    filename : str
        full filename with path
    bits : str
        sum or list of integers corresponding to all the bits to be reset

    Optional Parameters
    -------------------
    extver : int, optional
        List of version numbers of the arrays to be corrected
        (default: None, will reset all matching arrays)
    extname : str, optional
        EXTNAME of the arrays in the FITS files to be reset
        (default: 'dq')

    NOTES
    -----
    This module performs a simple bitwise-and on all the pixels in the specified
    array and the integer value provided as input using the operation (array & ~bits).

    Usage
    -----
    It can be called not only from within Python, but also from the host-level
    operating system command line using the syntax::

        resetbits filename bits [extver [extname]]


    EXAMPLES
    --------

    1. The following command will reset the 4096 bits in all
       the DQ arrays of the file 'input_flt.fits'::

            resetbits input_flt.fits 4096

       or from the Python command line::

            >>> import resetbits
            >>> resetbits.reset_dq_bits("input_file_flt.fits", 4096)


    2. To reset the 2,32,64 and 4096 (sum of 4194) bits in the
       second DQ array, specified as 'dq,2', in the file 'input_flt.fits'::

            resetbits input_flt.fits 4194 2

       or from the Python command line::

            >>> import resetbits
            >>> resetbits.reset_dq_bits("input_file_flt.fits", 2+32+64+4096, extver=2)

"""

from __future__ import division
import numpy as np
from stsci.tools import stpyfits as pyfits
from stsci.tools import parseinput, logutil

from . import util

__taskname__ = "drizzlepac.resetbits"
__version__ = '1.0.0'
__vdate__ = '3-Aug-2010'


log = logutil.create_logger(__name__)


def reset_dq_bits(input,bits,extver=None,extname='dq'):
    """ This function resets bits in the integer array(s) of a FITS file.

    Parameters
    ----------
    filename : str
        full filename with path

    bits : str
        sum or list of integers corresponding to all the bits to be reset

    extver : int, optional
        List of version numbers of the DQ arrays
        to be corrected [Default Value: None, will do all]

    extname : str, optional
        EXTNAME of the DQ arrays in the FITS file
        [Default Value: 'dq']

    Notes
    -----
    The default value of None for the 'extver' parameter specifies that all
    extensions with EXTNAME matching 'dq' (as specified by the 'extname'
    parameter) will have their bits reset.

    Examples
    --------
        1. The following command will reset the 4096 bits in all
           the DQ arrays of the file input_file_flt.fits::

                reset_dq_bits("input_file_flt.fits", 4096)

        2. To reset the 2,32,64 and 4096 bits in the second DQ array,
           specified as 'dq,2', in the file input_file_flt.fits::

                reset_dq_bits("input_file_flt.fits", "2,32,64,4096", extver=2)

    """
    # Interpret bits value 
    bits = util.interpret_bits_value(bits)
    
    flist, fcol = parseinput.parseinput(input)
    for filename in flist:
        # open input file in write mode to allow updating the DQ array in-place
        p = pyfits.open(filename,mode='update')

        # Identify the DQ array to be updated
        # If no extver is specified, build a list of all DQ arrays in the file
        if extver is None:
            extver = []
            for hdu in p:
                # find only those extensions which match the input extname
                # using case-insensitive name comparisons for 'extname'
                if hdu.header.has_key('extver') and \
                   hdu.header['extname'].lower() == extname.lower():
                    extver.append(int(hdu.header['extver']))
        else:
            # Otherwise, insure that input extver values are a list
            if not isinstance(extver, list): extver = [extver]

        # for each DQ array identified in the file...
        for extn in extver:
            dqarr = p[extname,extn].data
            # reset the desired bits
            p[extname,extn].data = (dqarr & ~bits).astype(np.int16)
            log.info('Reset bit values of %s to a value of 0 in %s[%s,%s]' %
                     (bits, filename, extname, extn))
        # close the file with the updated DQ array(s)
        p.close()

#
#### Interfaces used by TEAL
#
def run(configobj=None):
    ''' Teal interface for running this code. '''

    reset_dq_bits(configobj['input'],configobj['bits'],
                  extver=configobj['extver'],extname=configobj['extname'])

def getHelpAsString():
    helpString = 'resetbits Version '+__version__+'['+__vdate__+']\n'
    helpString += __doc__+'\n'

    return helpString

def help():
    print getHelpAsString()

def main():

    import getopt, sys

    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'h')
    except getopt.error, e:
        print str(e)
        print __doc__
        print "\t", __version__

    # initialize default values
    help = 0

    # read options
    for opt, value in optlist:
        if opt == "-h":
            help = 1

    if len(args) < 4:
        if len(args) < 3:
            args.append(None)
        args.append('dq')

    if (help):
        print __doc__
        print "\t", __version__+'('+__vdate__+')'
    else:
        reset_dq_bits(args[0],args[1],args[2], args[3])

if __name__ == "__main__":
    main()

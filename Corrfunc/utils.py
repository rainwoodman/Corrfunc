#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
from os.path import exists as file_exists

__all__ = ['translate_isa_string_to_enum', 'return_file_with_rbins',
           'fix_ra_dec', 'fix_cz', ]
if sys.version_info[0] < 3:
    __all__ = [n.encode('ascii') for n in __all__]


def return_file_with_rbins(rbins):
    """
    Helper function to ensure that the ``binfile`` required by the Corrfunc
    extensions is a actually a string.

    Checks if the input is a string and file; return if True. If not, and
    the input is an array, then a temporary file is created and the contents
    of rbins is written out.

    Parameters
    -----------
    rbins: string or array-like
       Expected to be a string or an array containing the bins
    
    Returns
    ---------
    binfile: string, filename
       If the input ``rbins`` was a valid filename, then returns the same
       string. If ``rbins`` was an array, then this function creates a
       temporary file with the contents of the ``rbins`` arrays. This
       temporary filename is returned

    """

    is_string = False
    delete_after_use = False
    try:
        if isinstance(rbins, basestring):
            is_string = True
    except NameError:
        if isinstance(rbins, str):
            is_string = True

    if is_string:
        if file_exists(rbins):
            delete_after_use = False
            return rbins, delete_after_use
        else:
            msg = "Could not find file = `{0}` containing the bins"\
                  .format(rbins)
            raise IOError(msg)

    # For a valid bin specifier, there must be at least 1 bin.
    if len(rbins) >= 1:
        import tempfile
        rbins = sorted(rbins)
        with tempfile.NamedTemporaryFile(delete=False) as f:
            for i in xrange(len(rbins)-1):
                f.write("{0} {1}\n".format(rbins[i], rbins[i+1]))

            tmpfilename = f.name

        delete_after_use = True
        return tmpfilename, delete_after_use

    msg = "Input `binfile` was not a valid array (>= 1 element)."\
          "Num elements = {0}".format(len(rbins))
    raise TypeError(msg)

    
def fix_cz(cz):
    """
    Multiplies the input array by speed of light, if the input values are
    too small.

    Essentially, converts redshift into `cz`, if the user passed
    redshifts instead of `cz`.

    Parameters
    -----------
    cz: array-like, reals
       An array containing ``[Speed of Light *] redshift`` values.
    
    Returns
    ---------
    cz: array-like
       Actual ``cz`` values, multiplying the input ``cz`` array by the
       ``Speed of Light``, if ``redshift`` values were passed as input ``cz``.
    
    """

    # if I find that max cz is smaller than this threshold,
    # then I will assume z has been supplied rather than cz
    max_cz_threshold = 10.0
    try:
        input_dtype = cz.dtype
    except:
        msg = "Input cz array must be a numpy array"
        raise TypeError(msg)
        
    if max(cz) < max_cz_threshold:
        speed_of_light = 299800.0
        cz *= speed_of_light

    return cz.astype(input_dtype)


def fix_ra_dec(ra, dec):
    """
    Wraps input RA and DEC values into range expected by the extensions.

    Parameters
    ------------
    RA: array-like, units must be degrees
       Right Ascension values (astronomical longitude)

    DEC: array-like, units must be degrees
       Declination values (astronomical latitude)

    Returns
    --------
    Tuple (RA, DEC): array-like
         RA is wrapped into range [0.0, 360.0]
         Declination is wrapped into range [-90.0, 90.0]

    """

    try:
        input_dtype = ra.dtype
    except:
        msg = "Input RA array must be a numpy array"
        raise TypeError(msg)
    
    if ra is None or dec is None:
        msg = "RA or DEC must be valid arrays"
        raise ValueError(msg)
    
    if min(ra) < 0.0:
        print("Warning: found negative RA values, wrapping into [0.0, 360.0] "
              " range")
        ra += 180.0

    if max(dec) > 90.0:
        print("Warning: found DEC values more than 90.0; wrapping into "
              "[-90.0, 90.0] range")
        dec += 90.0

    return ra.astype(input_dtype), dec.astype(input_dtype)


def translate_isa_string_to_enum(isa):
    """
    Helper function to convert an user-supplied string to the
    underlying enum in the C-API. The extensions only have specific
    implementations for AVX, SSE42 and FALLBACK. Any other value
    will raise a ValueError.
    
    Parameters
    ------------
    isa: string
       A string containing the desired instruction set. Valid values are
       ['AVX', 'SSE42', 'FALLBACK', 'FASTEST']
    
    Returns
    --------
    instruction_set: integer
       An integer corresponding to the desired instruction set, as used in the
       underlying C API. The enum used here should be defined *exactly* the
       same way as the enum in ``utils/defs.h``.

    """
    
    msg = "Input to translate_isa_string_to_enum must be "\
          "of string type. Found type = {0}".format(type(isa))
    try:
        if not isinstance(isa, basestring):
            raise TypeError(msg)
    except NameError:
        if not isinstance(isa, str):
            raise TypeError(msg)
    valid_isa = ['FALLBACK', 'AVX', 'SSE42', 'FASTEST']
    isa_upper = isa.upper()
    if isa_upper not in valid_isa:
        msg = "Desired instruction set = {0} is not in the list of valid "\
              "instruction sets = {1}".format(isa, valid_isa)
        raise ValueError(msg)
    
    enums = {'FASTEST': -1,
             'FALLBACK': 0,
             'SSE': 1,
             'SSE2': 2,
             'SSE3': 3,
             'SSSE3': 4,
             'SSE4': 5,
             'SSE42': 6,
             'AVX': 7,
             'AVX2': 8,
             'AVX512F': 9
             }
    try:
        return enums[isa_upper]
    except KeyError:
        print("Do not know instruction type = {0}".format(isa))
        print("Valid instructions are {0}".format(enums.keys()))
        raise
    


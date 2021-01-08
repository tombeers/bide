'''
    bide
    ----

    Easy, cross-platform interaction with paths, files and their content.

    :copyright: (c) 2016 by Tom Beers
    :licence: GPLv3, see licence.md for details
'''

from .utilities import Path, directory, compress, checksum, encode, decode
from .utilities import salt, feed
from .files import File

__package__ = 'bide'
__version__ = '0.2.0'

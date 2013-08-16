__doc_format__ = "reStructuredText"
'''
Shows info about netCDF on command line!

:Author: kmu
:Created: 18. jan. 2012
'''

''' Imports '''
# Built-in
import sys
execfile("../themes/set_pysenorge_path.py")
# Additional

# Own
from pysenorge.io.nc import NCreport

if len(sys.argv) != 2:
    print "USAGE: NCreport <path_to_netCDF_file>"
else:
    NCreport(sys.argv[1], stdout=True)
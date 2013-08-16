'''
This script tests which required and optional packages are available.

@author: kmu
@since: 7. okt. 2010
'''
import sys
print "Using Python version: %s" % sys.version
print "Operating system of type: %s" % sys.platform
print "Testing required packages..."
try:
    import numpy
    print "\t... numpy:\t OK"
except ImportError:
    print "\t... numpy not found"
try:
    import netCDF4
    print "\t... netCDF4:\t OK"
except ImportError:
    print "\t... netCDF4 not found"
try:
    import pyproj
    print "\t... pyproj:\t OK"
except ImportError:
    print "\t... pyproj not found"
    
print "Testing optional packages..."
try:
    import matplotlib
    print "\t... matplotlib:\t OK"
except ImportError:
    print "\t... matplotlib not found"
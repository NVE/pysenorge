__docformat__ = 'reStructuredText'
'''
Accumulated energy last 24h.
============================

Neglecting horizontal energy transfers as well as effects due to blowing snow
or vegetation, the balance for an open and flat snow cover is given in units
W m-2 by:

    net change rate of internal energy per unit area =
    short wave radiation downward +
    short wave radiation upward +
    long wave radiation downward +
    long wave radiation upward +
    sensible heat flux +
    latent heat flux +
    ground heat flux
    
:Note: Downward orientateted energy is taken as positive (energy gain). 

:Author: kmu
:Created: 29. nov. 2010
'''

''' IMPORTS '''
# Built-in
import os, time
import math
from datetime import timedelta
from optparse import OptionParser

# Adds folder containing the "pysenorge" package to the PYTHONPATH
execfile("set_pysenorge_path.py")

# Additional
try:
    from netCDF4 import Dataset
except ImportError:
    try:
        from Scientific.IO.NetCDF import NetCDFFile as Dataset
    except ImportError:
        print '''WARNING: Can not find module "netCDF4" or "Scientific.IO.NetCDF"!
        Please install for netCDF file support.'''
from numpy import sqrt, mean, flipud, zeros_like, arctan2, zeros, uint16

# Own
from pysenorge.set_environment import netCDFin, BILout, FloatFillValue, \
                                      UintFillValue
from pysenorge.io.bil import BILdata
from pysenorge.io.nc import NCdata
from pysenorge.io.png import writePNG
from pysenorge.tools.date_converters import iso2datetime, datetime2BILdate
from pysenorge.converters import nan2fill
from pysenorge.grid import interpolate
from pysenorge.functions.energy_flux import EnergyFluxBalance


def model(SWin, SWout, LWin, LWout, Hs, Hl, G=0.0):
    
    dH = EnergyFluxBalance(SWin, SWout, LWin, LWout, Hs, Hl, G=0.0)
    
    return dH
#! /usr/bin/python
'''Setup work environment

Contains the paths to the standard input/output folders and values used in L{pysenorge}.

@var BILin: Path to folder containing input data in .bil format.
@var BILout: Path to folder containing output data in .bil format.
@var netCDFin: Path to folder containing input data in netCDF format.
@var netCDFout: Path to folder containing output data in netCDF format.
@var PNGdir: Path to folder containing seNorge themes as PNG images.
@var pysenorgedir: Path to the pysenorge root folder.

@var UintFillValue: Standard value for no-data of type I{uint}.
@var IntFillValue: Standard value for no-data of type I{int}.
@var FloatFillValue: Standard value for no-data of type I{float}.

@var timeunit: Default start date for time values in seconds.

@author: kmu
@since: 16. aug. 2010
'''

#Build in modules
import sys
import os

if sys.platform == 'linux2':

    METdir = '/hdata/grid/metdata/metno_obs_v1.1/'

    PROGdir = '/hdata/drift/snowmap/pysenorge/'

    BILout = '/hdata/grid/snowsim/'

    netCDFin = '/hdata/grid/metdata/prognosis/harmonie/wind/netcdf/'

    netCDFout = '/hdata/grid/snowsim/'

    PNGdir = '/hdata/grid/snowsim/'

    LOGdir = '/hdata/grid/snowsim/'

elif sys.platform == 'win32':

    METdir = r'Z:\metdata\metno_obs_v1.1'

    PROGdir = r'Z:\metdata\prognosis'

    BILin = r'Z:\snowsim' # sorted by hydrological year
#    BILout = r'\\hdata\grid\snowsim'#
    BILout = r'Z:\snowsim'

    netCDFin = r'Z:\metdata\prognosis\um4'

    netCDFout = r'Z:\tmp'

    PNGdir = r'Z:\mapimage\png'

    LOGdir = r'Z:\log'

else:

    print "The current operating system is not supported!"

pysenorgedir = os.path.dirname(__file__)

UintFillValue = 65535
IntFillValue = 32767
FloatFillValue = 9.9692e+36

timeunit = "seconds since 1970-01-01 00:00:00 +00:00"

default_senorge_width = 1195
default_senorge_height = 1550

default_UM4_width = 533
default_UM4_height = 582

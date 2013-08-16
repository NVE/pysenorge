'''
Doc...

@author: kmu
@since: 1. nov. 2010
'''
# Built-in
import os
execfile("../themes/set_pysenorge_path.py") # Adds folder containing the "pysenorge" package to the PYTHONPATH @UnusedImport
# Additional
from numpy import flipud, int16
try:
    from netCDF4 import date2num
except ImportError:
    print '''WARNING: Can not find module "netCDF4"!
    Please install for netCDF file support.'''
# Own
from pysenorge.set_environment import timeunit
from pysenorge.io.bil import BILdata
from pysenorge.io.nc import NCdata
from pysenorge.tools.date_converters import get_date_filename, iso2datetime
from pysenorge.grid import senorge_mask
from pysenorge.converters import get_FillValue

def BIL2netCDF(BILfile, BILdtype='uint16', outdir=os.getcwd(), theme_name='undefined',
               theme_unit='undefined', long_name='undefined'):
    '''
    Convenience function converting the given BIL file to netCDF.
    
    @param BILfile: Input BIl file.
    @param outdir: Output directory.
    @param theme_name: Short name for the theme.   
    @param theme_unit: Metric unit of the theme data.
    @param long_name: Descriptive name for the theme. 
    
    @return: netCDF file in the output directory.
    '''
    ncfilename = os.path.splitext(os.path.basename(BILfile))[0] + '.nc'
    bd = BILdata(BILfile, BILdtype)
    bd.read()
    yy, mm, dd = get_date_filename(BILfile)
    tstring = yy+'-'+mm+'-'+dd+' 06:00:00'
    secs = date2num(iso2datetime(tstring), timeunit)
    mask = flipud(senorge_mask())
    ncdata = flipud(int16(bd.data)) # array needs to be flipped ud-down and transposed to fit the coordinate system
    ncdata[mask] = get_FillValue(ncdata.dtype)
    ncfile = NCdata(os.path.join(outdir, ncfilename))
#    ncfile.zip = True
    ncfile.new(secs)
    print ncdata.dtype.str
    ncfile.add_variable(theme_name, ncdata.dtype.str, theme_unit,
                        long_name, ncdata, lsd=1)
    ncfile.close()

def _test():
    BIL2netCDF(r'Z:\snowsim\swe\2000\swe_2000_01_27.bil', 'uint16', r'C:', 'swe', 'mm',
               'snow water equivalent')

if __name__ == '__main__':
    _test()
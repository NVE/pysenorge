# -*- coding:iso-8859-10 -*-
__docformat__ = 'restructuredtext'
'''
Doc...

:Author: kmu
:Created: 28. jan. 2011
'''
# Built-in
import os
execfile("../themes/set_pysenorge_path.py") # Adds folder containing the "pysenorge" package to the PYTHONPATH @UnusedImport
# Additional
from netCDF4 import Dataset, num2date
# Own
from pysenorge.set_environment import timeunit
from pysenorge.io.png import writePNG

def netCDF2PNG(ncfile, parameter, timendx=0, CLTfile=None, outdir=None):
    '''
    Convenience function converting a parameter in the given netCDF file to PNG.
    
    Parameters:
    ==========
    - ncfile: Input netCDF file.
    - parameter: parameter in netCDF file
    - outdir: Output directory. 
    
    Return:
    =======
    PNG file in the output directory.
    '''
    if outdir==None:
        outdir = os.path.dirname(os.path.abspath(ncfile))
    
    rootgrp = Dataset(ncfile, 'r')
    dt = num2date(rootgrp.variables['time'][timendx], timeunit).isoformat()
    print dt
    dt = dt.split('T')[0].replace('-','_')
    data = rootgrp.variables[parameter][timendx,:,:]
    
    # Write to PNG file
    writePNG(data, os.path.join(outdir, parameter+'_'+dt), CLTfile)

def _test():
    netCDF2PNG(r'Z:\tmp\wind_10m_daily\2011\wind_10m_daily_2011_02_02.nc',
               'wind_direction',
               CLTfile=r'Z:\tmp\wind_10m_daily\wind_direction_10_no.clt'
               )
    netCDF2PNG(r'Z:\tmp\wind_10m_daily\2011\wind_10m_daily_2011_02_02.nc',
               'avg_wind_speed',
               CLTfile=r'Z:\tmp\wind_10m_daily\avg_wind_speed_10_no.clt'
               )
    netCDF2PNG(r'Z:\tmp\wind_10m_daily\2011\wind_10m_daily_2011_02_02.nc',
               'max_wind_speed',
               CLTfile=r'Z:\tmp\wind_10m_daily\max_wind_speed_10_no.clt'
               )

if __name__ == '__main__':
    _test()
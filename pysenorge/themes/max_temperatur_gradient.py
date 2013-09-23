'''
Created on 13.09.2013

@author: RL

Creates a maximal temperatur-gradient map.

**To-Do**
-Load new nc file with a correct raster
-Export as bil or nc file

'''

#load hourly_temp
#check every cell where the steepest slope is in a 3 hrs intervall
#Save the maximum temperatur gradient
#create a new map
#with options --png and --bil

# Build-in
import os

# Additional
from numpy import zeros_like, absolute
try:
    from netCDF4 import Dataset
except ImportError:
    try:
        from Scientific.IO.NetCDF import NetCDFFile as Dataset
    except ImportError:
        print '''WARNING: Can not find module "netCDF4"
        or "Scientific.IO.NetCDF"!
        Please install for netCDF file support.'''

# Own
#execfile("set_pysenorge_path.py") # Adds folder containing the "pysenorge" package to the PYTHONPATH @UnusedImport
#from pysenorge.set_environment import METdir, BILout, netCDFout, IntFillValue, UintFillValue
#from pysenorge.grid import senorge_mask

path = "/home/ralf/Dokumente/summerjob/data/temp_netCDF/proff_default_NVE_00.nc"


class Mtg():

    '''
    Loads automatically the nc-file and stores the data
    in the variable "self.air_temp"
    '''
    def __init__(self):
        tmfile = os.path.join(path)
        ds = Dataset(tmfile, 'r')
        self.time = ds.variables['time'][:]
        self.air_temp = ds.variables['air_temperature'][:, :, :]
        self.latitude = ds.variables['latitude']
        self.longitude = ds.variables['longitude']
        ds.close()
        self.test, self.max = self.model(self.air_temp)

    def model(self, air_temp):
        '''
        Creates a grid of Norway with the maximal temperature gradient
        of a day. The maximal temperature gradient shows
        how fast temperatures are changed in a day. It is done
        by calculating the difference of the temperature
        in a three hours interval.
        '''
        dims = self.air_temp.shape
        a = zeros_like(self.air_temp[:, :, :])
        b = zeros_like(self.air_temp[0, :, :])
        for i in xrange(dims[1]):
            for j in xrange(dims[2]):
                li = []
                for k in xrange(24):
                    a[k, i, j] = self.air_temp[k, i, j] - self.air_temp[k + 3, i, j]
                    li.append(a[k, i, j])
                    b[i][j] = max(absolute(li))
        return a, b

if __name__ == "__main__":
    _mtg = Mtg()

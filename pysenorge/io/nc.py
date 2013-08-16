# -*- coding:iso-8859-10 -*-
__docformat__ = 'reStructuredtext'
'''
netCDF input/output classes.

netCDF fil standard for seNorge
===============================
    Grid data for seNorge.no (og kloner) skal lagres I netCDF fil format.
    
    
    Filer lagres med NETCDF3_CLASSIC flag, men med netCDF4 bibliotek. Dermed er
    det mulig og oppgrader til den nye standarden (basert på HDF5) til et senere
    tidspunkt.
    Versjon 4 av netCDF biblioteket tilbyr flere forbedringen som grupper, og
    flere datatyper. Filer lar seg komprimere. Dermed blir lese tilgangstiden
    redusert, men lagringsplass blir redusert betydelig.
    En senario er da at data blir komprimert etter en vist tid, så at aktuelle
    datasett er rask tilgjengelig, mens gamle (antagelig mindre brukte) ikke tar
    for mye plass.
    
    Filer med NETCDF3_CLASSIC flag bør ha en "group" attributt som henviser til
    en mulig framtidig implementert gruppe (som "observation, forecast, model,
    ...").


:Author: kmu
:Created: 14. okt. 2010
'''
# Built-in
import os, sys, time
sys.path.append(os.path.abspath('../..'))

# Additional
from numpy import arange, float32

try:
    from netCDF4 import Dataset, num2date
    print "Using netCDF4"
except ImportError:
    try:
        from Scientific.IO.NetCDF import NetCDFFile as Dataset
        print "Using Scientific.IO"
    except ImportError:
        print '''WARNING: Can not find module "netCDF4" or "Scientific.IO.NetCDF"!
        Please install one of them for netCDF file support.'''

# Own
from pysenorge.set_environment import timeunit, default_senorge_width,\
            default_senorge_height
from pysenorge.converters import get_FillValue
from pysenorge.grid import senorge_grid

class NCdata():
    """
    Class for reading, writing and displaying netCDF formated files for seNorge.no.
    """
    
    def __init__(self, filename):
        self.filename = filename
        
        self.default_senorge_time = 1
        
        self.zip = False
        
    
    def new(self, secs):
        """
        Creates a new seNorge netCDF file.
        Convention: Climate and Forecast (CF) version 1.4
        
        :Parameters:
            - secs: in seconds since 1970-01-01 00:00:00
        """
        # create new file
        try:
            rootgrp = Dataset(self.filename, 'w', format='NETCDF3_CLASSIC')
            # add root dimensions
            rootgrp.createDimension('time', size=self.default_senorge_time)
            rootgrp.createDimension('x', size=default_senorge_width)
            rootgrp.createDimension('y', size=default_senorge_height)
        except TypeError:
            rootgrp = Dataset(self.filename, 'w')
            # add root dimensions
            rootgrp.createDimension('time', self.default_senorge_time)
            rootgrp.createDimension('x', default_senorge_width)
            rootgrp.createDimension('y', default_senorge_height)
        
        # add root attributes
        rootgrp.Conventions = "CF-1.4"
        rootgrp.institution = "Norwegian Water Resources and Energy Directorate (NVE)"
        rootgrp.source = ""
        rootgrp.history = "%s created" % time.ctime(time.time())
        rootgrp.references = ""
        rootgrp.comment = "Data distributed via www.senorge.no"
        
        self.rootgrp = rootgrp
        
        # add coordinates
        try:
            times = self.rootgrp.createVariable('time', 'f8', ('time',))
        except TypeError:
            times = self.rootgrp.createVariable('time', 'f', ('time',))
        times.units = 'seconds since 1970-01-01 00:00:00 +00:00'
        times.long_name = 'time'
        times.standard_name = 'time'
        times.axis = 'T'
        times.calendar = 'standard'
        times[:] = secs
        
        self._set_utm()
        self._set_latlon()
        
        
    def add_variable(self, theme_name, theme_dtype, theme_unit, long_name, data,
                     lsd=None):
        """
        Creates a netCDF variable instances and adds data from a numpy.array to it.
        
        :Parameters:
            - theme_name: Abbreviation for the theme.
            - theme_dtype: Data-type in which the theme values should be stored.
            - theme_unit: SI unit of the data.
            - long_name: Decriptive name for the theme.
            - data: The input data to be stored.
            - lsd: Least significant digit to be stored.      
        """
        var = self.rootgrp.createVariable(theme_name, theme_dtype,
                                          ('time', 'y', 'x'),
                                          fill_value=get_FillValue(data.dtype),
                                          zlib=self.zip, # reduces disk space enormously 
                                          least_significant_digit=lsd
                                          )
        
        # set default attributes
        var.units = theme_unit
        var.long_name = long_name
        var._CoordinateSystems = "UTM_Projection"
        
        # Check for correct dimensions
        if data.shape == (1550, 1195):
            var[:] = data
        elif data.shape == (1195, 1550):
            var[:] = data.T
            print "Data array transposed before saving!"
        else:
            print "Data array does not have seNorge standard dimensions: (y=1550, x=1195)."
            self.close()
            
        print """Added variable "%s" to file %s""" % (theme_name, self.filename)
        
        
    def close(self):
        """
        Closes and flushes the netCDF file.
        """
        self.rootgrp.close()

    
    def report(self):
        """
        Writes a file report to the command line.
        """
        NCreport(self.rootgrp)    
    
    
    def _set_latlon(self):
        """
        Sets the latitude and longitude variables in the netCDF tree.
        """
        xgrid, ygrid, longrid, latgrid = senorge_grid(meshed=True) #@UnusedVariable
        
        try:
            lon = self.rootgrp.createVariable('lon', 'f4', ('y','x'),
                                              zlib=self.zip)
        except TypeError:
            lon = self.rootgrp.createVariable('lon', 'f', ('y','x'))
        lon.units = 'degrees_east'
        lon.long_name = 'longitude'
        lon.standard_name = 'longitude'
        lon[:] = float32(longrid)
        
        try:
            lat = self.rootgrp.createVariable('lat', 'f4', ('y','x'),
                                              zlib=self.zip)
        except TypeError:
            lat = self.rootgrp.createVariable('lat', 'f', ('y','x'))
        lat.units = 'degrees_north'
        lat.long_name = 'latitude'
        lat.standard_name = 'latitude'
        lat[:] = float32(latgrid)
        
        
    def _set_utm(self):
        """
        Sets the UTM coordinate variables in the netCDF tree.
        """
        # lower left corner in m
        LowerLeftEast = -75000
        LowerLeftNorth = 6450000
        # upper right corner in m
        UpperRightEast = 1120000
        UpperRightNorth = 8000000
        # x, y interval
        dx = 1000
        dy = 1000
        
#        proj = self.rootgrp.createVariable('ProjectionCoordinateSystem', 'c', ())
#        proj._CoordinateAxes = "y x"
#        proj._CoordinateTransforms = "UTM_Projection"
        
        utm = self.rootgrp.createVariable('UTM_Projection', 'c', ())
        utm.units = 'meters'
        utm.long_name = 'Universal Transverse Mercator Projection, Zone 33'
        utm.grid_mapping_name = "UTM"
        utm.scale_factor_at_central_meridian = 0.9996
        utm.latitude_of_projection_origin = 0
        utm.false_easting = 500000
        utm.utm_zone_number = 33
        utm.longitude_of_central_meridian = 15.0
        utm.semimajor_axis = 6378137.0
        utm.semi_minor_axis = 6356752.3142
        utm.proj4 = "+proj=utm +zone=33 +ellps=WGS84"
        utm._CoordinateTransformType = "Projection"
        utm._CoordinateAxes = "y x"
        utm._CoordinateAxisTypes = "GeoX GeoY"    
        
        try: 
            x = self.rootgrp.createVariable('x', 'f4', ('x',), zlib=self.zip)
        except TypeError:
            x = self.rootgrp.createVariable('x', 'f', ('x',))
        x.axis = 'X'
        x.units ='m'
        x.long_name = 'x coordinate of projection'
        x.standard_name = 'projection_x_coordinate'
        x._CoordinateAxisType = "GeoX"
        
        try:
            y = self.rootgrp.createVariable('y', 'f4', ('y',), zlib=self.zip)
        except TypeError:
            y = self.rootgrp.createVariable('y', 'f', ('y',))
        y.axis = 'Y'
        y.units ='m'
        y.long_name = 'y coordinate of projection'
        y.standard_name = 'projection_y_coordinate'
        y._CoordinateAxisType = "GeoY"
        
        x[:] = arange(LowerLeftEast, UpperRightEast, dx, dtype=float32)
        y[:] = arange(LowerLeftNorth, UpperRightNorth, dy, dtype=float32)


#class UM4Dataset(Dataset):
#    """
#    Class for reading, writing and displaying netCDF format files from met.no's 
#    UM4 model.
#    
#    Each file contains a +66 h prognosis.
#    The first value corresponds to the hour indicated in after the "UM4_sf" or
#    "UM4_ml".
#    Files with names "UM4_sf..." contain data with 1h time resolution.
#    Files with names "UM4_ml..." contain data with 6h time resolution
#    
#    """
#    def __info__(self):
#        print type(self)
#
#    def insert(self, master, mndx, tndx):
#        """
#        Insert a time series from master file at specified indices.
#        
#        @param master: netCDF4 I{Dataset} class object
#        @param mndx: boolean index of the master dataset 
#        @param tndx: boolean index of the target dataset
#        """
#        from pysenorge.tools.progress_bar import ProgressBar
#
#        Mdimensions = master.dimensions.keys() 
#        
#        # init the progress bar
#        pb = ProgressBar(len(master.variables.keys()))
#        count = 0
#        
#        # start inserting data        
#        for var in master.variables.keys():
#            count += 1 # only used for progressbar           
#            # exclude the variables referring to dimensions
#            if var not in Mdimensions:
#                dims = () # init dimension tuple before "exec" stmt
#                exec("dims = master.variables['%s'].dimensions" % (var))
#                if dims == ("time", "rlat", "rlon"):
#                    exec("M%s = master.variables['%s']" % (var, var))
#    #                exec("print '%s', master.variables['%s'].dimensions" % (var, var))
#                    exec("_%s = self.variables['%s']" % (var, var))
#                    pb.update(count, "Inserting %s data" % var)
#                    exec("_%s[tndx,:,:] = M%s[mndx,:,:]" % (var, var))
#                    
##        self.rootgrp.history += "\n%s data for period %s - %s inserted" %\
##            (time.ctime(time.time()),_start.isoformat(' '),_stop.isoformat(' '))
#
#
#class seNorgeDataset(Dataset):
#    """
#    Usage::
#        
#    """
#    def new(self, secs):
#        """
#        Creates a new seNorge netCDF file.
#        Convention: Climate and Forecast (CF) version 1.4
#        
#        @param secs: in seconds since 1970-01-01 00:00:00
#        """
#        # create new file
#        rootgrp = Dataset(self.filename, 'w', format='NETCDF3_CLASSIC')
#        
#        # add root dimensions
#        rootgrp.createDimension('time', size=self.default_senorge_time)
#        rootgrp.createDimension('x', size=default_senorge_width)
#        rootgrp.createDimension('y', size=default_senorge_height)
#        
#        # add root attributes
#        rootgrp.Conventions = "CF-1.4"
#        rootgrp.institution = "Norwegian Water Resources and Energy Directorate (NVE)"
#        rootgrp.source = ""
#        rootgrp.history = "%s created" % time.ctime(time.time())
#        rootgrp.references = ""
#        rootgrp.comment = "Data distributed via www.senorge.no"
#        
#        self.rootgrp = rootgrp
#        
#        # add coordinates
#        times = self.rootgrp.createVariable('time', 'f8', ('time',))
#        times.units = 'seconds since 1970-01-01 00:00:00 +00:00'
#        times.long_name = 'time'
#        times.standard_name = 'time'
#        times.axis = 'T'
#        times.calendar = 'standard'
#        times[:] = secs
#        
#        self._set_utm()
#        self._set_latlon()

class NCdataGrp(NCdata):
    '''
    UNDER CONSTRUCTION
    
    Collection of functions for reading, writing and displaying data stored in
    netCDF format version 4 supporting groups.
    
    
    The netCDF file contains three groups:
        - forecasts
        - observations
        - themes
        
    @warning: I{Groups} are a new feature in version 4. software based on
    version 3 will not be able to read these files. 
    '''
        
    def new(self):
        # create new file
        rootgrp = Dataset(self.filename, 'w', format='NETCDF4')
        # create standard groups
        fcstgrp = rootgrp.createGroup('forecasts')
        obsgrp = rootgrp.createGroup('observations')
        thmgrp = rootgrp.createGroup('themes')
        # add group attributes
        fcstgrp.long_name = 'weather_forecast'
        obsgrp.long_name = 'interpolated_observations'
        thmgrp.long_name = 'senorge_theme_layers'
        
        
        self.rootgrp = rootgrp
        self.fcstgrp = fcstgrp
        self.obsgrp = obsgrp
        self.thmgrp = thmgrp
        
        
    #Should there be a read and add function or just a general open function?
#    def open(self):
#        rootgrp = Dataset(self.filename, 'a')
        
    def add_forecast(self):
        pass
        
    def add_observation(self):
        pass
        
    def add_theme(self, theme_name, theme_dtype, theme_unit ):
        self.rootgrp = Dataset(self.filename, 'a') # might be replaced by open or add function
        self.rootgrp.thmgrp.createDimension(theme_name, size=self.default_theme_dimension)
        new_theme = self.rootgrp.thmgrp.createVariable(theme_name, theme_dtype, (theme_name,)) # check how the dimensions work for 2D!!!
        # set default attributes
        new_theme.units = theme_unit
        new_theme._FillValue = -32767.0 # make changeable and dependent on dtype
        
        
    def report(self):
        print self.rootgrp.groups
        
        
def NCreport(NCfile, stdout=False):
    """
    Might merge into NCdata.report
    """
    if isinstance(NCfile, Dataset):
        rootgrp = NCfile
    else:
        rootgrp = Dataset(NCfile, 'r')
    
    dimlist = rootgrp.dimensions.keys()
    varlist = rootgrp.variables.keys()
    timesteps = rootgrp.variables['time'].shape[0]
    if stdout:
        print "File: %s" % NCfile
        print "\tFlavor: %s" % rootgrp.file_format
        if "time" in dimlist:
            timesteps = rootgrp.variables['time'].shape[0]
            if timesteps > 1:
                print "\tTime-range: %s - %s\n\tTime-step: %.2f h" %\
                (num2date(rootgrp.variables['time'][0], timeunit),
                 num2date(rootgrp.variables['time'][timesteps-1], timeunit),
                 (rootgrp.variables['time'][1]-rootgrp.variables['time'][0])/3600.0
                 ) 
            else:
                print "\tTime: %s " %\
                num2date(rootgrp.variables['time'][0], timeunit)
        print "\tDimensions:"
        for dim in dimlist:
            print "\t\t%s" % dim
        print "\tVariables:"
        for var in varlist:
            print "\t\t%s" % var
        print "\n"
    rootgrp.close()
    return dimlist, varlist 


#def _test_netcdfUM4():    
#    '''
#    NCdataUM4 test function.
#    '''
#    # Set environment
#    ncdata = UM4Dataset(r"Z:\tmp\UM4sf_20100630_2.nc")
#
#    ncdata.clone(r"Z:\metdata\prognosis\UM4_for_snomodellering\201006\UM4sf_2010063000.nc",
#                 startdate="2010-06-29 07:00:00")
#    ncdata.insert(r"Z:\metdata\prognosis\UM4_for_snomodellering\201006\UM4sf_2010062900.nc",
#                  "2010-06-29 07:00:00", steps=18)
#    ncdata.insert(r"Z:\metdata\prognosis\UM4_for_snomodellering\201006\UM4sf_2010063000.nc",
#                  "2010-06-30 01:00:00", steps=6)
#    ncdata.close()
    
if __name__ == "__main__":
#    _test_netcdfUM4()
    NCreport(r"//hdata/grid/metdata/prognosis/um4/2011/UM4_ml00_2011_02_01.nc",
             stdout=True)
#    NCreport(r"Z:\tmp\average_wind_speed\2011\average_wind_speed_2011_01_31.nc",
#             stdout=True)
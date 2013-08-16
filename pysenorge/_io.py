'''
Input/output classes and functions.

@author: kmu
@since: 16. aug. 2010

@change: kmu, 2010-09-01, added class NCdata   
@change: kmu, 2010-09-06, added BILdata.write 
'''
# Built-in
import os, sys

# Additional
from numpy import arange, zeros, fromfile, uint16, int8, int16, float32, float64, flipud

try:
    from netCDF4 import Dataset, num2date, date2num #@UnusedImport
#    from scipy.io.netcdf import netcdf_file
except ImportError:
    print '''WARNING: Can not find module "netCDF4"! Install for netCDF file support.'''

# Own
from pysenorge.set_environment import UintFillValue, IntFillValue, FloatFillValue #@UnresolvedImport
from pysenorge.converters import date2epoch #@UnresolvedImport

class BILdata(object):
    '''
    Class for reading, writing and displaying BIL format files for U{www.senorge.no}.
    
    The seNorge array has a standard size of height=1550, width=1195.
    The standard data-type is "uint16" with a no-data-value of 65535.
    The standard file name is of type "themename_YYYY_MM_DD.bil"  
    '''


    def __init__(self, filename):
        '''
        Initializes defaults.
        '''
        self.nrows = 1550
        self.ncols = 1195
        self.datatype = uint16
        self.nodata = 65535
        self.data = zeros((self.nrows, self.ncols), self.datatype)
        self.filename = filename
        
        
    def set_dimension(self, nrows, ncols):
        '''
        Override standard dimensions.
        
        @param nrows: Number of new rows.
        @param ncols: Number of new columns.  
        '''
        self.nrows = nrows
        self.ncols = ncols
        
    
    def read(self):
        """
        Reads data from BIL file.
        """
        self._read_hdr()
        tmpdata = fromfile(self.filename, self.datatype)
        tmpdata.shape = (self.nrows, self.ncols)
        self.data[:] = tmpdata


    def _read_hdr(self):
        """
        Reads header information from I{.hdr} file (if existent).
        """
        hdr = os.path.splitext(self.filename)[0] + '.hdr'
        if os.path.exists(hdr):
            # Verify the information
            pass
        else:
            print "No header data found! Using default..."
            
            
    def write(self, data, dt=uint16, lsd=None):
        '''
        Writes data to BIL file.
        
        @param data: input numpy array to be stored
        @param dt: data-type, default is I{uint16}  
        @param lsd: Least significant digit
        @type lsd: integer 
        '''
        from types import IntType
        if type(lsd)==IntType:
            # Move the least significant digit before the dot.
            data = data * 10**lsd
        # Make sure data is appropriate format
        dt_data = dt(data)
        # Open and write to file
        fid = open(self.filename, 'wb')
        fid.write(dt_data)
        fid.flush()
        fid.close()
    
    
    def _write_hdr(self):
        ''' 
        Creates a I{.hdr} file to the corresponding I{.bil} file.
        
        NOT IMPLEMENTED YET!
         
        Example content of .hdr file
        BYTEORDER      I
        LAYOUT       BIL
        NROWS         1550
        NCOLS         1195
        NBANDS        1
        NBITS         16
        BANDROWBYTES         2390
        TOTALROWBYTES        2390
        BANDGAPBYTES         0
        '''
        pass    
        
        
    def _view(self):
        """
        Plot the data contained in the BIL file.
        @requires: I{Matplotlib} module
        """
        try:
            from matplotlib.pyplot import imshow, grid, colorbar, show
            from matplotlib.cm import jet
            
            imshow(self.data, interpolation='bilinear', cmap=jet, alpha=1.0)
            grid(False)
            colorbar()
            show()
            
        except ImportError:
            print '''Required plotting module "matplotlib" not found!\nVisit www.matplotlib.sf.net'''
            
            
def _test_bildata():
    '''
    BILdata test function.
    '''
    bd = BILdata(r'Z:\metdata\metno_obs_v1.1\tm\2006\tm_2006_01_04.bil')
    bd.read()
    bd.view()        


class NCdata():
    """
    Class for reading, writing and displaying netCDF format files for seNorge.no.
    
    
    @note: Mind the 4 GB restriction
    """
    
    def __init__(self, filename):
        self.filename = filename
        
        self.default_senorge_time = 1
        
        self.default_senorge_width = 1195
        self.default_senorge_height = 1550
        
        self.default_UM4_width = 533
        self.default_UM4_height =  582
        
        self.zip = False
        
    
    def new(self, secs):
        """
        Creates a new seNorge netCDF file.
        Convention: Climate and Forecast (CF) version 1.4
        
        @param secs: in seconds since 1970-01-01 00:00:00
        """
        # create new file
        rootgrp = Dataset(self.filename, 'w') # create new file using netcdf4
#        rootgrp = netcdf_file(self.filename, 'w') # create new file using scipy.IO
        
        # add root dimensions
        rootgrp.createDimension('time', size=self.default_senorge_time)
        rootgrp.createDimension('x', size=self.default_senorge_width)
        rootgrp.createDimension('y', size=self.default_senorge_height)
        
        # add root attributes
        rootgrp.Conventions = "CF-1.4"
        rootgrp.institution = "Norwegian Water Resources and Energy Directorate (NVE)"
        rootgrp.source = ""
        rootgrp.history = ""
        rootgrp.references = ""
        rootgrp.comment = "Data distributed via www.senorge.no"
        
        self.rootgrp = rootgrp
        
        # add coordinates
        time = self.rootgrp.createVariable('time', 'f8', ('time',))
        time.units = 'seconds since 1970-01-01 00:00:00 +00:00'
        time.long_name = 'time'
        time.standard_name = 'time'
        time[:] = secs
        
        self._set_utm()
        self._set_latlon()
        
        
    def add_variable(self, theme_name, theme_dtype, theme_unit, long_name, data, lsd=None):
        """
        Creates a netCDF variable instances and adds data from a numpy.array to it.
        
        @param theme_name: Abbreviation for the theme.
        @param theme_dtype: Data-type in which the theme values should be stored.
        @param theme_unit: SI unit of the data.
        @param long_name: Decriptive name for the theme.
        @param data: The input data to be stored.
        @type data: Numpy array
        @param lsd: Least significant digit to be stored.      
        """
        var = self.rootgrp.createVariable(theme_name, theme_dtype, ('time', 'y', 'x'),
                                          zlib=self.zip, least_significant_digit=lsd # reduces disk space enormously 
                                          )
        
        # set default attributes
        var.units = theme_unit
        var.long_name = long_name
        var._FillValue = self._getFillValue(data.dtype)
        var._CoordinateSystems = "UTM_Projection"
        
        # Check for correct dimensions
        if data.shape == (1550, 1195):
            var[:] = data
        elif data.shape == (1195, 1550):
            var[:] = data.T
        else:
            print "Data array does not have senorge standard dimensions: (1550, 1195)."
            self.close()
        
        
    def close(self):
        """
        Closes and flushes the netCDF file.
        """
        self.rootgrp.close()
        
        
    def _getFillValue(self, dt):
        """
        Determines the FillValue based on the data-type.
        
        No-data values are internally represented as numpy.nan values. These will be replaced by FillValues before writing to BIL or netCDF files. 
        """
        if dt == uint16:
            FillValue = uint16(UintFillValue)
        elif dt == int8:
            FillValue = int8(IntFillValue)
        elif dt == int16:
            FillValue = int16(IntFillValue)
        elif dt == float32:
            FillValue = float32(FloatFillValue)
        elif dt == float64:
            FillValue = float64(FloatFillValue)
        else:
            FillValue = dt(-9999)
        return FillValue

    
    def _set_latlon(self):
        """
        Sets the latitude and longitude variables in the netCDF tree.
        """
        lon = self.rootgrp.createVariable('lon', 'f4', ('x',), zlib=self.zip)
        lon.units = 'degrees_east'
        lon.long_name = 'longitude'
        lon.standard_name = 'longitude'
        
        lat = self.rootgrp.createVariable('lat', 'f4', ('y',), zlib=self.zip)
        lat.units = 'degrees_north'
        lat.long_name = 'latitude'
        lat.standard_name = 'latitude'
        
        
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
        
        x = self.rootgrp.createVariable('x', 'f4', ('x',), zlib=self.zip)
        x.axis = 'X'
        x.units ='m'
        x.long_name = 'x coordinate of projection'
        x.standard_name = 'projection_x_coordinate'
        x._CoordinateAxisType = "GeoX"
        
        y = self.rootgrp.createVariable('y', 'f4', ('y',), zlib=self.zip)
        y.axis = 'Y'
        y.units ='m'
        y.long_name = 'y coordinate of projection'
        y.standard_name = 'projection_y_coordinate'
        y._CoordinateAxisType = "GeoY"
        
        x[:] = arange(LowerLeftEast, UpperRightEast, dx)
        y[:] = arange(LowerLeftNorth, UpperRightNorth, dy)


def _test_netcdf():    
    '''
    NCdata test function.
    '''
    # Set environment
    pass


class NCdataGrp(NCdata):
    '''
    UNDER CONSTRUCTION
    
    Collection of functions for reading, writing and displaying data stored in netCDF file delivered by met.no.
    
    The netCDF file contains three groups:
        - forecasts
        - observations
        - themes
    '''
        
    def new(self):
        # create new file
        rootgrp = Dataset(self.filename, 'w') # create new file
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

         
def get_date(filename):
    """
    Splits the standard file name of type "themename_YYYY_MM_DD.bil/.nc" and extracts the date.
    @return: Strings: "YYYY", "MM", "DD"
    """
    filestr = os.path.splitext( os.path.basename(filename) )[0]
    strlist = filestr.split('_')
    yy = strlist[1]
    mm = strlist[2]
    dd = strlist[3]
    return yy, mm, dd
            
#def get_date(filename):
#    ds = Dataset(filename, 'r')
#    times = ds.variables['time']
#    print 'Reading time in '+times.units
#    dates = num2date(times[:],units=times.units, calendar='standard')
#    return dates

def find_date(datein='01.01.1970', timein='00:00:00s', dir=os.getcwd()):
    """
    Finds the netCDF file(s) that contain data from the input date and time.
    
    UNDER CONSTRUCTION
    
    @param datein: Input date of type DD.MM.YYYY
    @param timein: Input time of type HH:MM:SS
    @param dir: Directory in which to search through the netCDF files
    
    @return: File(s) containing the date/time, index of the time variable containing the date/time.
    """
    from glob import glob
    from datetime import datetime, date, time
    
    # Set date and time
    dsplit = datein.split('.')
    d = date(int(dsplit[2]), int(dsplit[1]), int(dsplit[0]))
    tsplit = timein.split(':')
    t = time(int(tsplit[2]), int(tsplit[1]), int(tsplit[0]))
    datec = datetime.combine(d,t)
    if dir is not os.getcwd():
        os.chdir(dir)
    filelist = glob('*.nc')
    print os.getcwd(), filelist
    for filename in filelist:
        ds = Dataset(filename, 'r')
        print 'ds okay'
        times = ds.variables['time']
        print 'times okay'
        time = date2num(datec, units=times.units, calendar='standard')
        print 'time okay', time
        print times[:]
#        if time in times[:]:
        ndx = times[:]==time
        print ndx
#            print 'ndx okay'
#            return filename, time, ndx
#        else:
#            print 'Given date and time not found in files.'
    
 
def BIL2netCDF(BILfile, outdir=os.getcwd(), theme_name='undefined', theme_unit='undefined', long_name='undefined'):
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
    bd = BILdata(BILfile)
    bd.read()
    yy, mm, dd = bd.get_date()
    tstring = yy+'-'+mm+'-'+dd+' 06:00:00'
    secs = date2epoch(tstring)

    ncdata = flipud(bd.data).T # array needs to be flipped ud-down and transposed to fit the coordinate system
    ncfile = NCdata(os.path.join(outdir, ncfilename))
#    ncfile.zip = True
    ncfile.new(secs)
    ncfile.add_variable(theme_name, bd.data.dtype, theme_unit, long_name, ncdata, lsd=0)
    ncfile.close()


def writePNG(A, outname):
    """
    Write PNG image using I{Matplotlib}.
    
    @param A: Input array containing the values to be plotted.
    @param outname: Name of the output image file. 
    """
    try:
        import matplotlib
        if sys.platform == 'linux2': 
            matplotlib.rcParams['backend'] = 'TkAgg' # set to common Tk backend to avoid conflicts on linux machine
        from matplotlib.pyplot import savefig, show, figure, colorbar
        
        # Plot resulting layer
        fig = figure(figsize=(11.95, 15.50))
        ax = fig.add_subplot(111)
        fig.subplots_adjust(left=0.0, bottom=0.0, right=1.0, top=1.0) 
        ax.imshow(A, vmin= -8, vmax=8)
        ax.axis('off')
        colorbar()
        savefig(outname+".png", dpi=100) # dpi x figsize = 1550x1195 pixel
        
        # Comment to suppress screen output
        show()
    
    except ImportError:
        print '''Required plotting module "matplotlib" not found!\nVisit www.matplotlib.sf.net''' 


def __writePNG(A, outname):
    """
    Write PNG image using the Python Image Library (PIL).
    
    UNDER CONSTRUCTION
    
    Would be faster and more flexible than using I{Matplotlib}.
    
    @param A: Input array containing the values to be plotted.
    @param outname: Name of the output image file. 
    """
    import Image, ImageColor
    im = Image.new('RGBA', (1195, 1550), ImageColor.colormap['firebrick'])
    print A.shape
    Am = Image.fromarray(A, 'RGBA')
    im.paste(Am)
    im.save(outname+'.png', 'PNG')
    
        
 
if __name__ == "__main__":
#    _test_bildata()
    BIL2netCDF(r'Z:\snowsim\swe\2000\swe_2000_01_27.bil', r'Z:\tmp', 'swe', 'mm', 'snow water equivalent')
#    BIL2netCDF('Z:\snowsim\swe\2000\swe_2000_01_27.bil', outdir='Z:\tmp', theme_name='swe', theme_unit'mm', long_name='snow water equivalent')

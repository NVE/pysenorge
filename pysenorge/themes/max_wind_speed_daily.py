'''
Calculates the maximum wind velocity based on hourly wind vector data.

A netcdf file with hourly data from 07:00 to 06:00 UTC serves as data source.
The amplitude of the hourly wind vectors is calculated for each cell. 
The amplitudes are then averaged over 24h. The result is interpolated from the 
4 km UM grid to the 1 km seNorge grid.

 
English name for theme: Maximum windspeed last 24h\n
Norsk navn for temalaget: Maksimum vindhastighet siste dogn

Command line usage
==================
    python //~/pysenorge/theme_layers/average_windspeed_daily.py YYYY-MM-DD
    [options]


@author: kmu
@since: 18. aug. 2010
'''

''' IMPORTS '''
# Built-in
import os, time
from optparse import OptionParser

# Adds folder containing the "pysenorge" package to the PYTHONPATH
execfile("set_pysenorge_path.py")

# Additional
from netCDF4 import Dataset
from numpy import sqrt, mean

# Own
from pysenorge.set_environment import netCDFin, netCDFout
from pysenorge.io.nc import NCdata
from pysenorge.tools.date_converters import iso2datetime, datetime2BILdate
from pysenorge.converters import nan2fill
from pysenorge.grid import interpolate

def model(x_wind, y_wind):
    
    wind_amp = sqrt(x_wind**2 + y_wind**2)
    return 

def main():
    # Theme variables
    themedir = 'awsd'
    themename = 'Average wind speed 24h'
    
    # Setup input parser
    usage = "usage: python //~HOME/pysenorge/theme_layers/average_windspeed_daily.py YYYY-MM-DD [options]"
    
    parser = OptionParser(usage=usage)
    parser.add_option("-o", "--outdir", 
                      action="store", dest="outdir", type="string",
                      default=os.path.join(netCDFout, themedir),
                      help="Output directory for netCDF file - default: $netCDFout/%s/$YEAR" % themedir)
    parser.add_option("-t", "--timerange", 
                      action="store", dest="timerange", type="string",
                      default="None",
                      help='''Time-range as "[6,30]"''')
    
    # Comment to suppress help
    parser.print_help()

    (options, args) = parser.parse_args()
    
    # Verify input parameters
    if len(args) != 1:
        parser.error("Please provide the date in ISO format YYYY-MM-DD!")
        parser.print_help() 
    
    # get current datetime
    cdt = iso2datetime(args[0]+" 06:00:00")
    ncfilename = "UM4_sf_%s.nc" % datetime2BILdate(cdt) # e.g. UM4_sf_2010_11_28.nc
    if len(args) != 1:
        parser.error("Please provide an input file!")
    else:
        # Add full path to the filename
        ncfile = os.path.join(netCDFin, str(cdt.year), ncfilename)
    
    timerange = eval(options.timerange)
    
    if not os.path.exists(ncfile):
        parser.error("%s does not exist!" % ncfile)
    else:
        if timerange == None:
            # Load wind data from prognosis (netCDF file) for full timerange
            ds = Dataset(ncfile, 'r')
            wind_time = ds.variables['time'][:]
            x_wind = ds.variables['x_wind'][:,:,:]
            y_wind = ds.variables['y_wind'][:,:,:]
            rlon = ds.variables['rlon'][:]
            rlat = ds.variables['rlat'][:]
            ds.close()    
            print "xwind-shape", x_wind.shape
        else:
            # Load wind data from prognosis (netCDF file) for selected timerange
            ds = Dataset(ncfile, 'r')
            wind_time = ds.variables['time'][timerange[0]:timerange[1]]
            x_wind = ds.variables['x_wind'][timerange[0]:timerange[1],:,:]
            y_wind = ds.variables['y_wind'][timerange[0]:timerange[1],:,:]
            rlon = ds.variables['rlon'][:]
            rlat = ds.variables['rlat'][:]
            ds.close()    
            print "xwind-shape", x_wind.shape

    
    # Setup outputs
    tstruct = time.gmtime(wind_time[-1]) # or -1 if it should be the average until that date
    outfile = '%s_%s_%s_%s' % (themedir, str(tstruct.tm_year).zfill(4),
                               str(tstruct.tm_mon).zfill(2),
                               str(tstruct.tm_mday).zfill(2))
    outdir = os.path.join(options.outdir, str(cdt.year))
    if not os.path.exists(outdir):
        if not os.path.exists(options.outdir):
            os.chdir(netCDFout)
            os.system('mkdir %s' % themedir)
        os.chdir(options.outdir)
        os.system('mkdir %s' % str(cdt.year))

    # Calculate the wind speed vector - using model()
    total_wind = model(x_wind, y_wind)
    # average over 24h
    total_wind_avg = mean(total_wind, axis=0)
    
    # interpolate total average wind speed to seNorge grid
    total_wind_avg_intp = interpolate(rlon, rlat, total_wind_avg)
    
    # Replace NaN values with the appropriate FillValue
    total_wind_avg_intp = nan2fill(total_wind_avg_intp)
    
    # Write to NC file
    ncfile = NCdata(os.path.join(outdir, outfile+'.nc'))
    ncfile.new(wind_time[0])
    
    ncfile.add_variable(themedir, total_wind_avg.dtype.str, "m s-1", themename, total_wind_avg_intp)
    ncfile.close()
    
    # At last - cross fingers it all worked out!
    print "\n*** Finished successfully ***\n"

if __name__ == '__main__':
    main()
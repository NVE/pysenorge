# -*- coding:utf-8 -*-
__docformat__ = 'reStructuredText'
'''
Calculates the average and maximal wind velocity as well as 6 hourly based wind
maps and a wind direction map. It is also possible to calculate the maximal dominant 
wind speed as well as hourly wind direction maps. But at the moment this maps and files
are not created.

A netcdf file with 24h of wind forecasts from the AROME-model serves as data source.
All calculations are made for a 1km raster over whole Norway for each cell. If no 
options are chosen the script produces .bil files as output. But its possible to
create netCDF file. The result is plotted in the seNorge grid. The argument 
timenc was added because the recent model delivers every 6 hours an output file. 
Therefore a second argument was needed to load the right file to the right time.

Command line usage:
===================
    python //~/pysenorge/themes/wind 1500m_daily.py YYYY-MM-DD timenc [options]

Daily production usage:
=======================
    python //~/pysenorge/themes/wind 1500m_daily.py YYYY-MM-DD 00
    python //~/pysenorge/themes/wind 1500m_daily.py YYYY-MM-DD 06
    python //~/pysenorge/themes/wind 1500m_daily.py YYYY-MM-DD 12
    python //~/pysenorge/themes/wind 1500m_daily.py YYYY-MM-DD 18

*Todo:*
- Make a test that checks that the 3-D matrix is multiplied correctly.

:Author: kmu
:Created: 28. jan. 2011
:Updated by RL on the 22. aug. 2013
'''

''' IMPORTS '''
#---------------------------------------------------------
# Built-in
#---------------------------------------------------------
import os
import time
import datetime

from optparse import OptionParser
#---------------------------------------------------------
# Additional modules
#---------------------------------------------------------
try:
    from netCDF4 import Dataset
except ImportError:
    try:
        from Scientific.IO.NetCDF import NetCDFFile as Dataset
    except ImportError:
        print '''WARNING: Can not find module "netCDF4" or "Scientific.IO.NetCDF"!
        Please install for netCDF file support.'''

execfile(os.path.join(os.path.dirname(__file__), "set_pysenorge_path.py"))

from numpy import flipud, uint16

#---------------------------------------------------------
# Own modules
#---------------------------------------------------------
from pysenorge.set_environment import netCDFin, BILout, \
                                      UintFillValue, netCDFout
from pysenorge.io.bil import BILdata
from pysenorge.io.nc import NCdata
from pysenorge.tools.date_converters import iso2datetime, get_hydroyear
from pysenorge.converters import nan2fill
from pysenorge.grid import interpolate_new
from pysenorge.functions.wind_model import model
from pysenorge.tools.get_timenc import _time_fun


#---------------------------------------------------------
#Main program
def main():
    """
    Loads and verifies input data, calls the model,\
    and controls the output stream.
    """

    # Setup input parser
    usage = "usage: python //~HOME/pysenorge/theme_layers/ \
            average_windspeed_daily.py YYYY-MM-DD NC-File-Describtion [options]"

#---------------------------------------------------------
    #add options with parser module
    parser = OptionParser(usage=usage)
    #create no bil
    parser.add_option("--no-bil",
                  action="store_false", dest="bil", default=True,
                  help="Set to suppress output in BIL format")
    #create netCDF
    parser.add_option("--nc",
                  action="store_true", dest="nc", default=False,
                  help="Set to store output in netCDF format")

    (options, args) = parser.parse_args()

    # Verify input parameters
    if len(args) != 2:
        parser.error("Please provide the date in ISO format YYYY-MM-DD and the timenc!")
        parser.print_help()

    # Select which date
    yr = str(args[0].split("-")[0])
    mon = str(args[0].split("-")[1])
    day = str(args[0].split("-")[2])

    # Select which nc-file
    timearg = args[1]

    load_date = "%s_%s_%s" % (yr, mon, day)
    tomorrow = (datetime.date(int(yr), int(mon), int(day)) +
                datetime.timedelta(days=1)).strftime("%Y_%m_%d")

    ncfilename = "AROME_WIND_850_NVE_%s_%s.nc" % (timearg, load_date)
    ncfile = os.path.join(netCDFin, yr, ncfilename)

    #Test if path of the netCDF file exists
    if not os.path.exists(ncfile):
        parser.error("%s does not exist!" % ncfile)
    else:
    # Load wind data from prognosis (netCDF file) for entire time-range
        ds = Dataset(ncfile, 'r')
        wind_time = ds.variables['time'][:]
        x_wind = ds.variables['x_wind_850hpa'][:, :, :]
        y_wind = ds.variables['y_wind_850hpa'][:, :, :]
        ds.close()

    print "Using input data from file %s" % ncfile

    # Get timenc and control if the time is right
    ob_time = time.strftime("%H", time.gmtime(wind_time[0]))
    timenc = _time_fun(ob_time)
    if timearg == timenc:
        pass
    else:
        print "WARNING! /n\
        The given input parameter and time value\
        of the netCDF are not the same"

    # Time range
    begin_time = time.strftime("%d-%m-%Y-%H:%M:%S", time.gmtime(wind_time[0]))
    end_time = time.strftime("%d-%m-%Y-%H:%M:%S", time.gmtime(wind_time[24]))

    print "For the period from the", begin_time, "to", end_time

    # For creation of hydroyear
    cdt = iso2datetime(args[0] + " 06:00:00")

#---------------------------------------------------------
    # Calculate the wind speed vector - using model()
    total_wind_avg, max_wind, total_wind, wind_dir_cat, \
    = model(x_wind, y_wind)

    # Interpolate total average wind speed to seNorge grid
    total_wind_avg_intp = interpolate_new(total_wind_avg)
    max_wind_intp = interpolate_new(max_wind)
    wind_dir_intp = interpolate_new(wind_dir_cat)
    #dom_wind_tab_intp = interpolate_new(dom_wind_tab)

    # Replace NaN values with the appropriate FillValue
    total_wind_avg_intp = nan2fill(total_wind_avg_intp)
    max_wind_intp = nan2fill(max_wind_intp)
    wind_dir_intp = nan2fill(wind_dir_intp)

#--------------------------------------------------------
    output_date = time.strftime("%Y_%m_%d", time.gmtime(wind_time[24]))

    # Arome 18 start time 00:00
    if timenc == "18":
        themedir1 = "wind_speed_1500m_avg_00"
        themedir2 = "wind_speed_1500m_max_00"
        themedir3 = "wind_speed_1500m_direction_00"
        themedir_direction = "wind_direction_1500m_00"

        outfile1 = '%s_%s' % (themedir1, output_date)
        outfile2 = '%s_%s' % (themedir2, output_date)
        outfile3 = '%s_%s' % (themedir3, output_date)

    # Hourly wind forecast based on the recent AROME input file
        themedir4 = "wind_speed_1500m_00"
        themedir5 = "wind_speed_1500m_06"
        themedir6 = "wind_speed_1500m_12"
        themedir7 = "wind_speed_1500m_18"

        wind_4 = interpolate_new(total_wind[0, :, :])
        wind_5 = interpolate_new(total_wind[6, :, :])
        wind_6 = interpolate_new(total_wind[12, :, :])
        wind_7 = interpolate_new(total_wind[18, :, :])

        outfile4 = '%s_%s' % ("wind_speed_1500m_00", load_date)
        outfile5 = '%s_%s' % ("wind_speed_1500m_06", load_date)
        outfile6 = '%s_%s' % ("wind_speed_1500m_12", load_date)
        outfile7 = '%s_%s' % ("wind_speed_1500m_18", load_date)

    # Arome 00 start time 06:00
    elif timenc == "00":
        themedir1 = "wind_speed_1500m_avg_06"
        themedir2 = "wind_speed_1500m_max_06"
        themedir3 = "wind_speed_1500m_direction_06"
        themedir_direction = "wind_direction_1500m_06"

        outfile1 = '%s_%s' % (themedir1, output_date)
        outfile2 = '%s_%s' % (themedir2, output_date)
        outfile3 = '%s_%s' % (themedir3, output_date)

    # Hourly wind forecast based on the recent AROME input file
        themedir4 = "wind_speed_1500m_06"
        themedir5 = "wind_speed_1500m_12"
        themedir6 = "wind_speed_1500m_18"
        themedir7 = "wind_speed_1500m_00"

        #model run at 00:00
        wind_4 = interpolate_new(total_wind[0, :, :])
        wind_5 = interpolate_new(total_wind[6, :, :])
        wind_6 = interpolate_new(total_wind[12, :, :])
        wind_7 = interpolate_new(total_wind[18, :, :])

        outfile4 = '%s_%s' % ("wind_speed_1500m_06", load_date)
        outfile5 = '%s_%s' % ("wind_speed_1500m_12", load_date)
        outfile6 = '%s_%s' % ("wind_speed_1500m_18", load_date)
        outfile7 = '%s_%s' % ("wind_speed_1500m_00", tomorrow)

    # Arome 06 start time 12:00
    elif timenc == "06":
        themedir1 = "wind_speed_1500m_avg_12"
        themedir2 = "wind_speed_1500m_max_12"
        themedir3 = "wind_speed_1500m_direction_12"
        themedir_direction = "wind_direction_1500m_12"

        outfile1 = '%s_%s' % (themedir1, output_date)
        outfile2 = '%s_%s' % (themedir2, output_date)
        outfile3 = '%s_%s' % (themedir3, output_date)

    # Hourly wind forecast based on the recent AROME input file
        themedir4 = "wind_speed_1500m_12"
        themedir5 = "wind_speed_1500m_18"
        themedir6 = "wind_speed_1500m_00"
        themedir7 = "wind_speed_1500m_06"

        wind_4 = interpolate_new(total_wind[0, :, :])
        wind_5 = interpolate_new(total_wind[6, :, :])
        wind_6 = interpolate_new(total_wind[12, :, :])
        wind_7 = interpolate_new(total_wind[18, :, :])

        outfile4 = '%s_%s' % ("wind_speed_1500m_12", load_date)
        outfile5 = '%s_%s' % ("wind_speed_1500m_18", load_date)
        outfile6 = '%s_%s' % ("wind_speed_1500m_00", tomorrow)
        outfile7 = '%s_%s' % ("wind_speed_1500m_06", tomorrow)

    # Arome 12 start time 18:00
    elif timenc == "12":
        themedir1 = "wind_speed_1500m_avg_18"
        themedir2 = "wind_speed_1500m_max_18"
        themedir3 = "wind_speed_1500m_direction_18"
        themedir_direction = "wind_direction_1500m_18"

        outfile1 = '%s_%s' % (themedir1, output_date)
        outfile2 = '%s_%s' % (themedir2, output_date)
        outfile3 = '%s_%s' % (themedir3, output_date)

    # Hourly wind forecast based on the recent AROME input File
        themedir4 = "wind_speed_1500m_18"
        themedir5 = "wind_speed_1500m_00"
        themedir6 = "wind_speed_1500m_06"
        themedir7 = "wind_speed_1500m_12"

        wind_4 = interpolate_new(total_wind[0, :, :])
        wind_5 = interpolate_new(total_wind[6, :, :])
        wind_6 = interpolate_new(total_wind[12, :, :])
        wind_7 = interpolate_new(total_wind[18, :, :])

        outfile4 = '%s_%s' % ("wind_speed_1500m_18", load_date)
        outfile5 = '%s_%s' % ("wind_speed_1500m_00", tomorrow)
        outfile6 = '%s_%s' % ("wind_speed_1500m_06", tomorrow)
        outfile7 = '%s_%s' % ("wind_speed_1500m_12", tomorrow)

    #----------------------------------------------------------------
    # Output path wind_speed_1500m_avg
    outdir1 = os.path.join(BILout, themedir1, str(get_hydroyear(cdt)))
    if not os.path.exists(outdir1):
        if not os.path.exists(os.path.join(BILout, themedir1)):
            os.chdir(BILout)
            os.makedirs('%s' % themedir1)
        os.chdir(os.path.join(BILout, themedir1))
        os.makedirs('%s' % str(get_hydroyear(cdt)))

    # Output path wind_speed_1500m_max
    outdir2 = os.path.join(BILout, themedir2, str(get_hydroyear(cdt)))
    if not os.path.exists(outdir2):
        if not os.path.exists(os.path.join(BILout, themedir2)):
            os.chdir(BILout)
            os.makedirs('%s' % themedir2)
        os.chdir(os.path.join(BILout, themedir2))
        os.makedirs('%s' % str(get_hydroyear(cdt)))

    # Output path wind_speed_1500m_direction
    outdir3 = os.path.join(BILout, themedir_direction, str(get_hydroyear(cdt)))
    if not os.path.exists(outdir3):
        if not os.path.exists(os.path.join(BILout, themedir_direction)):
            os.chdir(BILout)
            os.makedirs('%s' % themedir_direction)
        os.chdir(os.path.join(BILout, themedir_direction))
        os.makedirs('%s' % str(get_hydroyear(cdt)))

    # Output path 4
    outdir4 = os.path.join(BILout, themedir4, str(get_hydroyear(cdt)))
    if not os.path.exists(outdir4):
        if not os.path.exists(os.path.join(BILout, themedir4)):
            os.chdir(BILout)
            os.makedirs('%s' % themedir4)
        os.chdir(os.path.join(BILout, themedir4))
        os.makedirs('%s' % str(get_hydroyear(cdt)))

    # Output path 5
    outdir5 = os.path.join(BILout, themedir5, str(get_hydroyear(cdt)))
    if not os.path.exists(outdir5):
        if not os.path.exists(os.path.join(BILout, themedir5)):
            os.chdir(BILout)
            os.makedirs('%s' % themedir5)
        os.chdir(os.path.join(BILout, themedir5))
        os.makedirs('%s' % str(get_hydroyear(cdt)))

    # Output path 6
    outdir6 = os.path.join(BILout, themedir6, str(get_hydroyear(cdt)))
    if not os.path.exists(outdir6):
        if not os.path.exists(os.path.join(BILout, themedir6)):
            os.chdir(BILout)
            os.makedirs('%s' % themedir6)
        os.chdir(os.path.join(BILout, themedir6))
        os.makedirs('%s' % str(get_hydroyear(cdt)))

    # Output path 7
    outdir7 = os.path.join(BILout, themedir7, str(get_hydroyear(cdt)))
    if not os.path.exists(outdir7):
        if not os.path.exists(os.path.join(BILout, themedir7)):
            os.chdir(BILout)
            os.makedirs('%s' % themedir7)
        os.chdir(os.path.join(BILout, themedir7))
        os.makedirs('%s' % str(get_hydroyear(cdt)))

#---------------------------------------------------------
    # Option --bil: Multiplied by 10 to store data as integer
    if options.bil:
        from pysenorge.grid import senorge_mask
        mask = senorge_mask()

        # Wind_speed_1500m_avg
        bil_avg_wind = flipud(uint16(total_wind_avg_intp * 10.0))
        bil_avg_wind[mask] = UintFillValue

        bilfile = BILdata(os.path.join(outdir1,
                          outfile1 + '.bil'),
                          datatype='uint16')
        biltext = bilfile.write(bil_avg_wind.flatten())
        print biltext

        # Wind_speed_1500m_max
        bil_max_wind = flipud(uint16(max_wind_intp * 10.0))
        bil_max_wind[mask] = UintFillValue
        bilfile = BILdata(os.path.join(outdir2,
                          outfile2 + '.bil'),
                          datatype='uint16')
        biltext = bilfile.write(bil_max_wind.flatten())
        print biltext

        # Wind_speed_1500m_direction
        bil_dir_wind = flipud(uint16(wind_dir_intp * 10))
        bil_dir_wind[mask] = UintFillValue
        bilfile = BILdata(os.path.join(outdir3,
                          outfile3 + '.bil'),
                          datatype='uint16')
        biltext = bilfile.write(bil_dir_wind.flatten())
        print biltext

        # Wind_speed at 00:00
        bil_wind_00 = flipud(uint16(wind_4 * 10.0))
        bil_wind_00[mask] = UintFillValue
        bilfile = BILdata(os.path.join(outdir4,
                          outfile4 + '.bil'),
                          datatype='uint16')
        biltext = bilfile.write(bil_wind_00.flatten())
        print biltext

        # Wind_speed at 06:00
        bil_wind_06 = flipud(uint16(wind_5 * 10.0))
        bil_wind_06[mask] = UintFillValue
        bilfile = BILdata(os.path.join(outdir5,
                          outfile5 + '.bil'),
                          datatype='uint16')
        biltext = bilfile.write(bil_wind_06.flatten())
        print biltext

        # Wind_speed at 12:00
        bil_wind_12 = flipud(uint16(wind_6 * 10.0))
        bil_wind_12[mask] = UintFillValue
        bilfile = BILdata(os.path.join(outdir6,
                          outfile6 + '.bil'),
                          datatype='uint16')
        biltext = bilfile.write(bil_wind_12.flatten())
        print biltext

        # Wind_speed at 18:00
        bil_wind_18 = flipud(uint16(wind_7 * 10.0))
        bil_wind_18[mask] = UintFillValue
        bilfile = BILdata(os.path.join(outdir7,
                          outfile7 + '.bil'),
                          datatype='uint16')
        biltext = bilfile.write(bil_wind_18.flatten())
        print biltext

#---------------------------------------------------------
    # Option --nc: write a nc file
    if options.nc:
        ncfile = NCdata(os.path.join(netCDFout, outfile1 + '.nc'))

        ncfile.new(wind_time[-1])

        ncfile.add_variable('avg_wind_speed', total_wind_avg.dtype.str, "m s-1",
                             'Average wind speed last 24h', total_wind_avg_intp)
        ncfile.add_variable('max_wind_speed', max_wind.dtype.str, "m s-1",
                             'Maximum wind gust last 24h', max_wind_intp)
        ncfile.add_variable('wind_direction', wind_dir_cat.dtype.str,
                             "cardinal direction",
                             'Prevailing wind direction last 24h',
                              wind_dir_intp)
        ncfile.add_variable(themedir4, wind_4.dtype.str, "m s-1",
                             'Wind forecast', wind_4)
        ncfile.add_variable(themedir5, wind_5.dtype.str, "m s-1",
                             'Wind forecast', wind_5)
        ncfile.add_variable(themedir6, wind_6.dtype.str, "m s-1",
                             'Wind forecast', wind_6)
        ncfile.add_variable(themedir7, wind_7.dtype.str, "m s-1",
                             'Wind forecast', wind_7)

        ncfile.close()

    # At last - cross fingers* it all worked out! *and toes !!!
    print "\n***Finished successfully***\n"

if __name__ == '__main__':
    main()

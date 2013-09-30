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
create netCDF or PNG files. The result is plotted in the seNorge grid. The argument 
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
from pysenorge.set_environment import netCDFin, BILout, FloatFillValue, \
                                      UintFillValue
from pysenorge.io.bil import BILdata
from pysenorge.io.nc import NCdata
from pysenorge.io.png import writePNG
from pysenorge.tools.date_converters import iso2datetime, get_hydroyear
from pysenorge.converters import nan2fill
from pysenorge.grid import interpolate_new
from pysenorge.functions.wind_model import model
from pysenorge.tools.get_timenc import _time_fun


#---------------------------------------------------------
#Main program
def main():
    """
    Loads and verifies input data, calls the model, and controls the output stream.
    """

    # Theme variables
    themedir1 = 'wind_speed_avg_1500m'
    themedir2 = 'wind_speed_max_1500m'

    today = datetime.date.today().strftime("%Y_%m_%d")
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y_%m_%d")

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
    #create png
    parser.add_option("--png",
                  action="store_true", dest="png", default=False,
                  help="Set to store output as PNG image")

#   Comment to suppress help
#   parser.print_help()
    (options, args) = parser.parse_args()

    # Verify input parameters
    if len(args) != 2:
        parser.error("Please provide the date in ISO format YYYY-MM-DD and the timenc!")
        parser.print_help()

    #Select which date
    yr = str(args[0].split("-")[0])
    mon = str(args[0].split("-")[1])
    day = str(args[0].split("-")[2])

    #Select which nc-file
    timearg = args[1]

    load_date = "%s_%s_%s" % (yr, mon, day)

    ncfilename = "AROME_WIND_850_NVE_%s_%s.nc" % (timearg, load_date)
    ncfile = os.path.join(netCDFin, "2013", ncfilename)

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

    #Get timenc and control if the time is right
    ob_time = time.strftime("%H", time.gmtime(wind_time[0]))
    data_timenc = _time_fun(ob_time)
    if timearg == data_timenc:
        pass
    else:
        print "The given input parameter and time value of the netCDF are not the same"
    timenc = data_timenc

#---------------------------------------------------------
    #Output paths, output filenames and timerange
    begin_time = time.strftime("%d-%m-%Y-%H:%M:%S", time.gmtime(wind_time[0]))
    end_time = time.strftime("%d-%m-%Y-%H:%M:%S", time.gmtime(wind_time[24]))

    print "For the period from the", begin_time, "to", end_time

    outfile1 = '%s_%s' % (themedir1, today)
    outfile2 = '%s_%s' % (themedir2, today)

    cdt = iso2datetime(args[0] + " 06:00:00")

#---------------------------------------------------------
    #Output path 1
    outdir1 = os.path.join(BILout, themedir1, str(get_hydroyear(cdt)))
    if not os.path.exists(outdir1):
        if not os.path.exists(os.path.join(BILout, themedir1)):
            os.chdir(BILout)
            os.system('mkdir %s' % themedir1)
        os.chdir(os.path.join(BILout, themedir1))
        os.system('mkdir %s' % str(get_hydroyear(cdt)))

    #Output path 2
    outdir2 = os.path.join(BILout, themedir2, str(get_hydroyear(cdt)))
    if not os.path.exists(outdir2):
        if not os.path.exists(os.path.join(BILout, themedir2)):
            os.chdir(BILout)
            os.system('mkdir %s' % themedir2)
        os.chdir(os.path.join(BILout, themedir2))
        os.system('mkdir %s' % str(get_hydroyear(cdt)))

    #Output path for wind_00 til wind _18
    if timenc == "00":
        outdir_hour = os.path.join(BILout, str(get_hydroyear(cdt)), load_date, "00")
    elif timenc == "06":
        outdir_hour = os.path.join(BILout, str(get_hydroyear(cdt)), load_date, "06")
    elif timenc == "12":
        outdir_hour = os.path.join(BILout, str(get_hydroyear(cdt)), load_date, "12")
    elif timenc == "18":
        outdir_hour = os.path.join(BILout, str(get_hydroyear(cdt)), load_date, "18")

    if not os.path.exists(outdir_hour):
        if not os.path.exists(os.path.join(BILout, str(get_hydroyear(cdt)))):
            os.chdir(BILout)
            os.system('mkdir %s' % str(get_hydroyear(cdt)))
        os.chdir(os.path.join(BILout, str(get_hydroyear(cdt))))
        os.makedirs('%s/%s/' % (load_date, timenc))

#---------------------------------------------------------
    # Calculate the wind speed vector - using model()
    total_wind_avg, max_wind, total_wind, wind_dir_cat, \
    hour_wind = model(x_wind, y_wind)

    # interpolate total average wind speed to seNorge grid
    total_wind_avg_intp = interpolate_new(total_wind_avg)
    max_wind_intp = interpolate_new(max_wind)
    wind_dir_intp = interpolate_new(wind_dir_cat)
    #dom_wind_tab_intp = interpolate_new(dom_wind_tab)

    # Replace NaN values with the appropriate FillValue
    total_wind_avg_intp = nan2fill(total_wind_avg_intp)
    max_wind_intp = nan2fill(max_wind_intp)
    wind_dir_intp = nan2fill(wind_dir_intp)
    #dom_wind_tab_intp = nan2fill(dom_wind_tab_intp)

#--------------------------------------------------------
    #Hourly wind forecast based on the recent AROME input file
    if timenc == "18":
    #at 01:00
        wind_18 = interpolate_new(total_wind[0, :, :])
        hour_wind_intp_18 = interpolate_new(hour_wind[0, :, :])
    #at 07:00
        wind_00 = interpolate_new(total_wind[6, :, :])
        hour_wind_intp_00 = interpolate_new(hour_wind[6, :, :])
    #at 13:00
        wind_06 = interpolate_new(total_wind[12, :, :])
        hour_wind_intp_06 = interpolate_new(hour_wind[12, :, :])
    #at 19:00
        wind_12 = interpolate_new(total_wind[18, :, :])
        hour_wind_intp_12 = interpolate_new(hour_wind[18, :, :])

        outfile3 = '%s_%s' % ("wind_speed_18_1500m", today)
        outfile4 = '%s_%s' % ("wind_speed_00_1500m", today)
        outfile5 = '%s_%s' % ("wind_speed_06_1500m", today)
        outfile6 = '%s_%s' % ("wind_speed_12_1500m", today)

    elif timenc == "00":
    #at 07:00
        wind_00 = interpolate_new(total_wind[0, :, :])
        hour_wind_intp_00 = interpolate_new(hour_wind[0, :, :])
    #at 13:00
        wind_06 = interpolate_new(total_wind[6, :, :])
        hour_wind_intp_06 = interpolate_new(hour_wind[6, :, :])
    #at 19:00
        wind_12 = interpolate_new(total_wind[12, :, :])
        hour_wind_intp_12 = interpolate_new(hour_wind[12, :, :])
    #next day at 01:00
        wind_18 = interpolate_new(total_wind[18, :, :])
        hour_wind_intp_18 = interpolate_new(hour_wind[18, :, :])

        outfile3 = '%s_%s' % ("wind_speed_00_1500m", today)
        outfile4 = '%s_%s' % ("wind_speed_06_1500m", today)
        outfile5 = '%s_%s' % ("wind_speed_12_1500m", today)
        outfile6 = '%s_%s' % ("wind_speed_18_1500m", tomorrow)

    elif timenc == "06":
        #at 13:00
        wind_06 = interpolate_new(total_wind[0, :, :])
        hour_wind_intp_06 = interpolate_new(hour_wind[0, :, :])
        #at 19:00
        wind_12 = interpolate_new(total_wind[6, :, :])
        hour_wind_intp_12 = interpolate_new(hour_wind[6, :, :])
        #next day 01:00
        wind_18 = interpolate_new(total_wind[12, :, :])
        hour_wind_intp_18 = interpolate_new(hour_wind[12, :, :])
        #next day 07:00
        wind_00 = interpolate_new(total_wind[18, :, :])
        hour_wind_intp_00 = interpolate_new(hour_wind[18, :, :])

        outfile3 = '%s_%s' % ("wind_speed_06_1500m", today)
        outfile4 = '%s_%s' % ("wind_speed_12_1500m", today)
        outfile5 = '%s_%s' % ("wind_speed_18_1500m", tomorrow)
        outfile6 = '%s_%s' % ("wind_speed_00_1500m", tomorrow)

    elif timenc == "12":
        #at 19:00
        wind_12 = interpolate_new(total_wind[0, :, :])
        hour_wind_intp_12 = interpolate_new(hour_wind[0, :, :])
        #next day 01:00
        wind_18 = interpolate_new(total_wind[6, :, :])
        hour_wind_intp_18 = interpolate_new(hour_wind[6, :, :])
        #next day 07:00
        wind_00 = interpolate_new(total_wind[12, :, :])
        hour_wind_intp_00 = interpolate_new(hour_wind[12, :, :])
        #next day 13:00
        wind_06 = interpolate_new(total_wind[18, :, :])
        hour_wind_intp_06 = interpolate_new(hour_wind[18, :, :])

        outfile3 = '%s_%s' % ("wind_speed_12_1500m", today)
        outfile4 = '%s_%s' % ("wind_speed_18_1500m", tomorrow)
        outfile5 = '%s_%s' % ("wind_speed_00_1500m", tomorrow)
        outfile6 = '%s_%s' % ("wind_speed_06_1500m", tomorrow)

#---------------------------------------------------------
    #Option --bil: Multiplied by 10 to store data as integer
    if options.bil:
        from pysenorge.grid import senorge_mask
        mask = senorge_mask()

        #Avg wind
        bil_avg_wind = flipud(uint16(total_wind_avg_intp * 10.0))
        bil_avg_wind[mask] = UintFillValue

        bilfile = BILdata(os.path.join(outdir1,
                          outfile1 + '.bil'),
                          datatype='uint16')
        #Colapse into one dimension
        biltext = bilfile.write(bil_avg_wind.flatten())
        print biltext

        # Max wind
        bil_max_wind = flipud(uint16(max_wind_intp * 10.0))
        bil_max_wind[mask] = UintFillValue
        bilfile = BILdata(os.path.join(outdir2,
                          outfile2 + '.bil'),
                          datatype='uint16')
        biltext = bilfile.write(bil_max_wind.flatten())
        print biltext

        # bil wind at 00
        bil_wind_00 = flipud(uint16(wind_00 * 10.0))
        bil_wind_00[mask] = UintFillValue
        bilfile = BILdata(os.path.join(outdir_hour,
                          outfile3 + '.bil'),
                          datatype='uint16')
        biltext = bilfile.write(bil_wind_00.flatten())
        print biltext

        # bil wind at 06
        bil_wind_06 = flipud(uint16(wind_06 * 10.0))
        bil_wind_06[mask] = UintFillValue
        bilfile = BILdata(os.path.join(outdir_hour,
                          outfile4 + '.bil'),
                          datatype='uint16')
        biltext = bilfile.write(bil_wind_06.flatten())
        print biltext

        #bil wind at 12
        bil_wind_12 = flipud(uint16(wind_12 * 10.0))
        bil_wind_12[mask] = UintFillValue
        bilfile = BILdata(os.path.join(outdir_hour,
                          outfile5 + '.bil'),
                          datatype='uint16')
        biltext = bilfile.write(bil_wind_12.flatten())
        print biltext

        #bil wind at 18
        bil_wind_18 = flipud(uint16(wind_18 * 10.0))
        bil_wind_18[mask] = UintFillValue
        bilfile = BILdata(os.path.join(outdir_hour,
                          outfile6 + '.bil'),
                          datatype='uint16')
        biltext = bilfile.write(bil_wind_18.flatten())
        print biltext

#---------------------------------------------------------
    #Option --nc: write a nc file
    if options.nc:
        ncfile = NCdata(os.path.join(outdir1, outfile1 + '.nc'))

        ncfile.new(wind_time[-1])

        ncfile.add_variable('avg_wind_speed', total_wind_avg.dtype.str, "m s-1",
                             'Average wind speed last 24h', total_wind_avg_intp)
        ncfile.add_variable('max_wind_speed', max_wind.dtype.str, "m s-1",
                             'Maximum wind gust last 24h', max_wind_intp)
        ncfile.add_variable('wind_direction', wind_dir_cat.dtype.str,
                             "cardinal direction",
                             'Prevailing wind direction last 24h', wind_dir_intp)
        ncfile.add_variable('wind_00', wind_00.dtype.str, "m s-1",
                             'Wind forecast 01:00', wind_00)
        ncfile.add_variable('wind_06', wind_06.dtype.str, "m s-1",
                             'Wind forecast 07:00', wind_06)
        ncfile.add_variable('wind_12', wind_12.dtype.str, "m s-1",
                             'Wind forecast 13:00', wind_12)
        ncfile.add_variable('wind_18', wind_18.dtype.str, "m s-1",
                             'Wind forecast 19:00', wind_18)

        ncfile.close()

#---------------------------------------------------------
    #Option --png: Write a PNG files
    if options.png:
        avg_clt_file_path = "/home/ralf/Dokumente/summerjob/data/avg_wind_speed_10_no.clt"
        max_clt_file_path = "/home/ralf/Dokumente/summerjob/data/max_wind_speed_10_no.clt"
        direction_clt_file_path = "/home/ralf/Dokumente/summerjob/data/wind_direction_10_no.clt"

        #Creates png file wind average
        writePNG(total_wind_avg_intp[:, :],
                os.path.join(outdir1, outfile1),
                 cltfile=avg_clt_file_path
                 )

        #Creates png file wind max
        writePNG(max_wind_intp[:, :],
                 os.path.join(outdir2, outfile2),
                 cltfile=max_clt_file_path
                 )

        #Hourly wind speed maps
        writePNG(wind_00,
                os.path.join(outdir_hour, outfile3),
                cltfile=avg_clt_file_path
                )

        writePNG(wind_06,
                os.path.join(outdir_hour, outfile4),
                cltfile=avg_clt_file_path
                )

        writePNG(wind_12,
                os.path.join(outdir_hour, outfile5),
                cltfile=avg_clt_file_path
                )

        writePNG(wind_18,
                os.path.join(outdir_hour, outfile6),
                cltfile=avg_clt_file_path
                )

        #Wind direction
        writePNG(wind_dir_intp[:, :],
                  os.path.join(outdir1, 'wind_direction'),
                  cltfile=direction_clt_file_path
                  )

        #Hourly wind directions
        writePNG(hour_wind_intp_00[:, :],
                os.path.join(outdir1, 'wind_direction_hour_00'),
                cltfile=direction_clt_file_path
                )

        writePNG(hour_wind_intp_06[:, :],
                os.path.join(outdir1, 'wind_direction_hour_06'),
                cltfile=direction_clt_file_path
                )

        writePNG(hour_wind_intp_12[:, :],
                os.path.join(outdir1, 'wind_direction_hour_12'),
                cltfile=direction_clt_file_path
                )

        writePNG(hour_wind_intp_18[:, :],
                os.path.join(outdir1, 'wind_direction_hour_18'),
                cltfile=direction_clt_file_path
                )

        #Maximal dominate wind speed
        #writePNG(dom_wind_tab_intp[:, :],
        #          os.path.join(outdir1, today, 'wind_direction_dom_wind_tab'),
        #          cltfile=direction_clt_file_path
        #          )
    # At last - cross fingers* it all worked out! *and toes !!!
    print "\n***Finished successfully***\n"

if __name__ == '__main__':
    main()

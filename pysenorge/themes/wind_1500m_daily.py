# -*- coding:utf-8 -*-
__docformat__ = 'reStructuredText'
'''
Calculates the average wind velocity based on hourly wind vector data.

A netcdf file with hourly data from 07:00 to 06:00 UTC serves as data source.
The amplitude of the hourly wind vectors is calculated for each cell. 
The amplitudes are then averaged over 24h. The result is plotted in the 1 km seNorge grid.

English name for theme: Average windspeed last 24h\n
Norsk navn for temalaget: Gjennomsnittlig vindhastighet siste dogn

Command line usage:
===================
    python //~/pysenorge/themes/wind 10m_daily.py YYYY-MM-DD [options]
    
Daily production usage:
=======================
    python //~/pysenorge/themes/wind 10m_daily.py YYYY-MM-DD --no-bil --nc 
    -t

*Todo:*
- Make a test that checks that the 3-D matrix is multiplied correctly.
- Add a theme showing max wind gust last 24 h.
- Add a theme showing prevailing wind direction last 24 h.

- Make dependent on wind direction. Read wind direction - determine 
    predominant wind direction - calculated average wind speed in predominant 
    wind direction (avg all wind speed might give false alarm). Wind directions 
    can be classified in either 4 or 8 regions (90 or 45 degrees).


:Author: kmu
:Created: 28. jan. 2011
:Updated by RL on the 22. aug. 2013
'''

''' IMPORTS '''
#---------------------------------------------------------    
# Built-in
#---------------------------------------------------------    
import os, time
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
from numpy import sqrt, mean, flipud, zeros_like, arctan2, zeros, uint16, degrees, amax, where

execfile(os.path.join(os.path.dirname(__file__), "set_pysenorge_path.py"))

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
from pysenorge.functions.lamberts_formula import LambertsFormula

#---------------------------------------------------------    
#import timenc from the Arome Data
#---------------------------------------------------------    
 
#---------------------------------------------------------    
#Define wind model
#---------------------------------------------------------    
def model(x_wind, y_wind):
    """
    Calculates avg. and max. wind speed and prevailing wind direction from the
    x and y vector components.
      
    :Parameters:
        - x_wind: Wind vector component in *x*-direction
        - y_wind: Wind vector component in *y*-direction
    """    
    
    total_wind = sqrt(x_wind**2 + y_wind**2)
    dims = total_wind.shape
    total_wind_avg = mean(total_wind, axis=0)
    wind_dir_cat = zeros_like(total_wind_avg)
    wind_dir = arctan2(y_wind, x_wind)
      
    print "Wind-data dimensions:", dims
    
#---------------------------------------------------------    
#Create max wind vector
    max_wind = amax(total_wind[0:24,0:dims[1],0:dims[2]],axis=0)
    new_wind_dir = degrees(wind_dir)

    W = new_wind_dir[(new_wind_dir>=-22.5) & (new_wind_dir<22.5)]
    SW = new_wind_dir[(new_wind_dir>=22.5) & (new_wind_dir<67.5)]
    S = new_wind_dir[(new_wind_dir>=67.5) & (new_wind_dir<112.5)]
    SE = new_wind_dir[(new_wind_dir>=112.5) & (new_wind_dir<157.5)]
    NW = new_wind_dir[(new_wind_dir>-22.5) & (new_wind_dir<=-67.5)]
    N = new_wind_dir[(new_wind_dir>-67.5) & (new_wind_dir<=-112.5)]
    NE = new_wind_dir[(new_wind_dir>-112.5) & (new_wind_dir<=-157.5)]
    E = new_wind_dir[(new_wind_dir<-157.5) | (new_wind_dir>=157.5) ]
      
    wind_dir_cat[:,:] = LambertsFormula(len(N),len(NE),len(E),len(SE),len(S),len(SW),len(W),len(NW))
    
#---------------------------------------------------------    
#Daily wind directions with 45 degrees
    #W
    hour_wind_dir = where((new_wind_dir>=-22.5) & (new_wind_dir<22.5),6, new_wind_dir)
    #SW
    hour_wind_dir = where((hour_wind_dir>=22.5) & (hour_wind_dir<67.5),5, hour_wind_dir)
    #S
    hour_wind_dir = where((hour_wind_dir>=67.5) & (hour_wind_dir<112.5),4, hour_wind_dir)
    #SE
    hour_wind_dir = where((hour_wind_dir>=112.5) & (hour_wind_dir<157.5),3, hour_wind_dir)
    #NW
    hour_wind_dir = where((hour_wind_dir>-22.5) & (hour_wind_dir<=-67.5),7, hour_wind_dir)
    #N
    hour_wind_dir = where((hour_wind_dir>-67.5) & (hour_wind_dir<=-112.5),0, hour_wind_dir)
    #NE
    hour_wind_dir = where((hour_wind_dir>-112.5) & (hour_wind_dir<=-157.5),1, hour_wind_dir)
    #E
    hour_wind_dir = where((hour_wind_dir<-157.5) | (hour_wind_dir>=157.5) ,2, hour_wind_dir)
     
#---------------------------------------------------------    
#Return values
    return total_wind_avg, max_wind, total_wind, wind_dir_cat, hour_wind_dir

#---------------------------------------------------------    
#Start main program
#---------------------------------------------------------    
def main():
    """
    Loads and verifies input data, calls the model, and controls the output stream. 
    
    Command line usage::
    
        python //~HOME/pysenorge/themes/wind_10m_daily.py YYYY-MM-DD [options]
    """
#---------------------------------------------------------    
#Timenc variable is comes from the inputdata and should be according to the Aromemodell
#either "00","06","12","18"
    
    timenc = "00"
    
    # Theme variables
    themedir1 = 'wind_speed_avg_1500m' 
    themedir2 = 'wind_speed_max_1500m'
    
    # Setup input parser
    usage = "usage: python //~HOME/pysenorge/theme_layers/average_windspeed_daily.py YYYY-MM-DD [options]"

#---------------------------------------------------------
#add options with parser module
#---------------------------------------------------------    
    #timerange
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--timerange", 
                      action="store", dest="timerange", type="string",
                      default="[0,24]",
                      help='''Time-range as "[6,30]"''')
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
    if len(args) != 1:
        parser.error("Please provide the date in ISO format YYYY-MM-DD!")
        parser.print_help() 
    
    #ncfile = os.path.join(netCDFin, "2013", ncfilename)
    ncfile = "/home/ralf/Dokumente/summerjob/data/2013/AROME_WIND_850_%s_NVE.nc" %timenc
    
    timerange = eval(options.timerange)
    #timerange = None
    
    print 'Time-range', timerange
    #test if path of the netCDF file exists
    if not os.path.exists(ncfile):
        parser.error("%s does not exist!" % ncfile)
    else:
        if timerange == None:
            # Load wind data from prognosis (netCDF file) for entire time-range
            ds = Dataset(ncfile, 'r')
            wind_time = ds.variables['time'][:]
            x_wind = ds.variables['x_wind_850hpa'][:,:,:]
            y_wind = ds.variables['y_wind_850hpa'][:,:,:]
            ds.close()
        else:
            # Load wind data from prognosis (netCDF file) for selected time-range
            ds = Dataset(ncfile, 'r')
            wind_time = ds.variables['time'][timerange[0]:timerange[1]]
            x_wind = ds.variables['x_wind_850hpa'][timerange[0]:timerange[1],:,:]
            y_wind = ds.variables['y_wind_850hpa'][timerange[0]:timerange[1],:,:]
            ds.close()
    
    print "Using input data from file %s" % ncfile

#---------------------------------------------------------
#Output paths and output filenames  
#---------------------------------------------------------    
    _tstart = time.gmtime(wind_time[0])
    tstruct = time.gmtime(wind_time[-1]) # or -1 if it should be the average until that date
    begin_time = time.strftime("%d-%m-%Y-%H:%M:%S", time.gmtime(wind_time[0]))
    end_time = time.strftime("%d-%m-%Y-%H:%M:%S", time.gmtime(wind_time[23]))
    
    print "For the period from the",begin_time ,"to", end_time
    
    outfile1 = '%s_%s_%s_%s' % (themedir1, str(tstruct.tm_year).zfill(4),
                               str(tstruct.tm_mon).zfill(2),
                               str(tstruct.tm_mday).zfill(2))
    outfile2 = '%s_%s_%s_%s' % (themedir2, str(tstruct.tm_year).zfill(4),
                               str(tstruct.tm_mon).zfill(2),
                               str(tstruct.tm_mday).zfill(2))
    
    cdt = iso2datetime(args[0]+" 06:00:00")

#---------------------------------------------------------
#Output path 1  
    outdir1 = os.path.join(BILout, themedir1, str(get_hydroyear(cdt)))
    if not os.path.exists(outdir1):
        if not os.path.exists(os.path.join(BILout, themedir1)):
            os.chdir(BILout)
            os.system('mkdir %s' % themedir1)
        os.chdir(os.path.join(BILout, themedir1))
        os.system('mkdir %s' % str(get_hydroyear(cdt)))

#---------------------------------------------------------
#Output path 2 
    outdir2 = os.path.join(BILout, themedir2, str(get_hydroyear(cdt)))
    if not os.path.exists(outdir2):
        if not os.path.exists(os.path.join(BILout, themedir2)):
            os.chdir(BILout)
            os.system('mkdir %s' % themedir2)
        os.chdir(os.path.join(BILout, themedir2))
        os.system('mkdir %s' % str(get_hydroyear(cdt)))
#---------------------------------------------------------
#Output path for wind_00 til wind _18
    outdir_hour = os.path.join(BILout, str(get_hydroyear(cdt)), "current")
    if not os.path.exists(outdir_hour):
        if not os.path.exists(os.path.join(BILout, str(get_hydroyear(cdt)))):
            os.chdir(BILout)
            os.system('mkdir %s' % "current")
        os.chdir(os.path.join(BILout, str(get_hydroyear(cdt))))
        os.system('mkdir %s' % "current")

#---------------------------------------------------------
#Output filename for wind_00 til wind _18
    outfile3 = '%s_%s_%s_%s_%s' % ("wind_00","hourly_1500m", str(tstruct.tm_year).zfill(4),
                               str(tstruct.tm_mon).zfill(2),
                               str(tstruct.tm_mday).zfill(2))

    outfile4 = '%s_%s_%s_%s_%s' % ("wind_06","hourly_1500m", str(tstruct.tm_year).zfill(4),
                                   str(tstruct.tm_mon).zfill(2),
                                   str(tstruct.tm_mday).zfill(2))
    
    outfile5 = '%s_%s_%s_%s_%s' % ("wind_12","hourly_1500m", str(tstruct.tm_year).zfill(4),
                                   str(tstruct.tm_mon).zfill(2),
                                   str(tstruct.tm_mday).zfill(2))
    
    outfile6 = '%s_%s_%s_%s_%s' % ("wind_18","hourly_1500m", str(tstruct.tm_year).zfill(4),
                                   str(tstruct.tm_mon).zfill(2),
                                   str(tstruct.tm_mday).zfill(2))

#---------------------------------------------------------
#Clip wind data to SEnorge grid 
#---------------------------------------------------------    
    # Calculate the wind speed vector - using model() 
    total_wind_avg, max_wind, total_wind, wind_dir_cat, hour_wind = model(x_wind, y_wind) 
    
    # interpolate total average wind speed to seNorge grid
    total_wind_avg_intp = interpolate_new(total_wind_avg)
    max_wind_intp = interpolate_new(max_wind)
    wind_dir_intp = interpolate_new(wind_dir_cat)

    # Replace NaN values with the appropriate FillValue
    total_wind_avg_intp = nan2fill(total_wind_avg_intp)
    max_wind_intp = nan2fill(max_wind_intp)
    wind_dir_intp = nan2fill(wind_dir_intp)

#--------------------------------------------------------
#Current wind prognosis based on the newest AROME input file
#--------------------------------------------------------
    if timenc == "00":
    #at 00:00
        wind_00 = interpolate_new(total_wind[0,:,:])
        hour_wind_intp_00 = interpolate_new(hour_wind[0,:,:])
    #at 06:00
        wind_06 = interpolate_new(total_wind[6,:,:])
        hour_wind_intp_06 = interpolate_new(hour_wind[6,:,:])
    #at 12:00
        wind_12 = interpolate_new(total_wind[12,:,:])
        hour_wind_intp_12 = interpolate_new(hour_wind[12,:,:])
    #at 18:00
        wind_18 = interpolate_new(total_wind[18,:,:])
        hour_wind_intp_18 = interpolate_new(hour_wind[18,:,:])

    elif timenc == "06":
    #at 06:00
        wind_06 = interpolate_new(total_wind[0,:,:])
        hour_wind_intp_06 = interpolate_new(hour_wind[0,:,:])
    #at 12:00
        wind_12 = interpolate_new(total_wind[6,:,:])
        hour_wind_intp_12 = interpolate_new(hour_wind[6,:,:])
    #at 18:00
        wind_18 = interpolate_new(total_wind[12,:,:])
        hour_wind_intp_18 = interpolate_new(hour_wind[12,:,:])
    #at 00:00
        wind_00 = interpolate_new(total_wind[18,:,:])
        hour_wind_intp_00 = interpolate_new(hour_wind[18,:,:])
    
    elif timenc == "12":
    #at 12:00
        wind_12 = interpolate_new(total_wind[0,:,:])
        hour_wind_intp_12 = interpolate_new(hour_wind[0,:,:])
    #at 18:00
        wind_18 = interpolate_new(total_wind[6,:,:])
        hour_wind_intp_18 = interpolate_new(hour_wind[6,:,:])
    #at 00:00
        wind_00 = interpolate_new(total_wind[12,:,:])
        hour_wind_intp_00 = interpolate_new(hour_wind[12,:,:])
    #at 06:00
        wind_06 = interpolate_new(total_wind[18,:,:])
        hour_wind_intp_06 = interpolate_new(hour_wind[18,:,:])
    
    elif timenc == "18":
    #at 18:00
        wind_18 = interpolate_new(total_wind[0,:,:])
        hour_wind_intp_18 = interpolate_new(hour_wind[0,:,:])
    #at 00:00
        wind_00 = interpolate_new(total_wind[6,:,:])
        hour_wind_intp_00 = interpolate_new(hour_wind[6,:,:])
    #at 06:00
        wind_06 = interpolate_new(total_wind[12,:,:])
        hour_wind_intp_06 = interpolate_new(hour_wind[12,:,:])
    #at 12:00
        wind_12 = interpolate_new(total_wind[18,:,:])
        hour_wind_intp_12 = interpolate_new(hour_wind[18,:,:])
    
#---------------------------------------------------------
#Option --bil => Multiplied by 10 to store data as integer
#---------------------------------------------------------    
    if options.bil:
        from pysenorge.grid import senorge_mask
        
        mask = senorge_mask()
 
#---------------------------------------------------------     
        #avg wind
        bil_avg_wind = flipud(uint16(total_wind_avg_intp*10.0))
        bil_avg_wind[mask] = UintFillValue
         
        bilfile = BILdata(os.path.join(outdir1,
                          outfile1+'.bil'),
                          datatype='uint16')
        biltext = bilfile.write(bil_avg_wind.flatten()) # collapsed into one dimension
        print biltext
#---------------------------------------------------------    
        #  max wind
        bil_max_wind = flipud(uint16(max_wind_intp*10.0))
        bil_max_wind[mask] = UintFillValue
        bilfile = BILdata(os.path.join(outdir2,
                          outfile2+'.bil'),
                          datatype='uint16')
        biltext = bilfile.write(bil_max_wind.flatten())
        print biltext
#---------------------------------------------------------    
        # bil wind at 00
        bil_wind_00 = flipud(uint16(wind_00*10.0))
        bil_wind_00[mask] = UintFillValue
        bilfile = BILdata(os.path.join(outdir_hour,
                          outfile3+'.bil'),
                          datatype='uint16')
        biltext = bilfile.write(bil_wind_00.flatten())
        print biltext
#---------------------------------------------------------    
        # bil wind at 06
        bil_wind_06 = flipud(uint16(wind_06*10.0))
        bil_wind_06[mask] = UintFillValue
        bilfile = BILdata(os.path.join(outdir_hour,
                          outfile4+'.bil'),
                          datatype='uint16')
        biltext = bilfile.write(bil_wind_06.flatten())
        print biltext
#---------------------------------------------------------    
        #bil wind at 12
        bil_wind_12 = flipud(uint16(wind_12*10.0))
        bil_wind_12[mask] = UintFillValue
        bilfile = BILdata(os.path.join(outdir_hour,
                          outfile5+'.bil'),
                          datatype='uint16')
        biltext = bilfile.write(bil_wind_12.flatten())
        print biltext
#---------------------------------------------------------    
        #bil wind at 18
        bil_wind_18 = flipud(uint16(wind_18*10.0))
        bil_wind_18[mask] = UintFillValue
        bilfile = BILdata(os.path.join(outdir_hour,
                          outfile6+'.bil'),
                          datatype='uint16')
        biltext = bilfile.write(bil_wind_18.flatten())
        print biltext

#---------------------------------------------------------
#Option --nc write a nc file
#---------------------------------------------------------    
    if options.nc:
        ncfile = NCdata(os.path.join(outdir1, outfile1+'.nc'))
  
        ncfile.new(wind_time[-1])
          
        ncfile.add_variable('avg_wind_speed', total_wind_avg.dtype.str, "m s-1",
                             'Average wind speed last 24h', total_wind_avg_intp)
        ncfile.add_variable('max_wind_speed', max_wind.dtype.str, "m s-1",
                             'Maximum wind gust last 24h', max_wind_intp)
        ncfile.add_variable('wind_direction', wind_dir_cat.dtype.str,
                             "cardinal direction",
                             'Prevailing wind direction last 24h', wind_dir_intp)
        ncfile.close()

#---------------------------------------------------------
#Option --png Write a PNG file
#---------------------------------------------------------    
    if options.png:
#----------------------------------------------------
        #null inside index removed
        writePNG(total_wind_avg_intp[:,:],
                os.path.join(outdir1, outfile1),
                 cltfile=r"/home/ralf/Dokumente/summerjob/data/avg_wind_speed_10_no.clt"
                 )
       
        #null inside index removed
        writePNG(max_wind_intp[:,:],
                 os.path.join(outdir2, outfile2),
                 cltfile=r"/home/ralf/Dokumente/summerjob/data/max_wind_speed_10_no.clt"
                 )
        
        #6hour Norgemaps windspeed
        writePNG(wind_00,
                 os.path.join(outdir_hour, outfile3),
                 cltfile=r"/home/ralf/Dokumente/summerjob/data/avg_wind_speed_10_no.clt"
                 )  

        writePNG(wind_06,
                  os.path.join(outdir_hour, outfile4),
                  cltfile=r"/home/ralf/Dokumente/summerjob/data/avg_wind_speed_10_no.clt"
                  )  
        
        writePNG(wind_12,
                  os.path.join(outdir_hour, outfile5),
                  cltfile=r"/home/ralf/Dokumente/summerjob/data/avg_wind_speed_10_no.clt"
                  )  
        
        writePNG(wind_18,
                  os.path.join(outdir_hour, outfile6),
                  cltfile=r"/home/ralf/Dokumente/summerjob/data/avg_wind_speed_10_no.clt"
                  )  

        #Wind direction
        writePNG(wind_dir_intp[:,:],
                  os.path.join(outdir1, 'wind_direction'),
                  cltfile=r"/home/ralf/Dokumente/summerjob/data/wind_direction_10_no.clt"
                  )
    
        #6hour Norgemaps winddirection
        writePNG(hour_wind_intp_00[:,:],
                  os.path.join(outdir1, 'wind_direction_hour_00'),
                  cltfile=r"/home/ralf/Dokumente/summerjob/data/wind_direction_10_no.clt"
                  )
        
        writePNG(hour_wind_intp_06[:,:],
                  os.path.join(outdir1, 'wind_direction_hour_06'),
                  cltfile=r"/home/ralf/Dokumente/summerjob/data/wind_direction_10_no.clt"
                  )
        
        writePNG(hour_wind_intp_12[:,:],
                  os.path.join(outdir1, 'wind_direction_hour_12'),
                  cltfile=r"/home/ralf/Dokumente/summerjob/data/wind_direction_10_no.clt"
                  )
        
        writePNG(hour_wind_intp_18[:,:],
                  os.path.join(outdir1, 'wind_direction_hour_18'),
                  cltfile=r"/home/ralf/Dokumente/summerjob/data/wind_direction_10_no.clt"
                  )

    # At last - cross fingers* it all worked out! *and toes !!! 
    print "\n*** Finished successfully ***\n"


def __clt_avg_wind_speed_no():
    from pysenorge.io.png import CLT, HDR, CLTitem
    hdr = HDR(255, 8,
              'Gjennomsnittlig vindhastighet',
              'Gjennomsnittlig vindhastighet i 10 m h�yde',
              'Vindstyrke')
    cltlist = [CLTitem(36.7, 300.0, (255,74,74), 'Orkan (over 32,6 m/s)'),
               CLTitem(28.5, 32.6, (126, 0, 255), 'Sterk storm (28,5-32,6 m/s)'),
               CLTitem(24.5, 28.4, (255,194,74), 'Full storm (24,5-28,4 m/s)'),
               CLTitem(20.8, 24.4, (255,255,74), 'Liten storm (20,8-24,4 m/s)'),
               CLTitem(17.2, 20.7, (194,224,74), 'Sterk kuling (17,2-20,7 m/s)'),
               CLTitem(13.9, 17.1, (134,194,74), 'Stiv kuling (13,9-17,1 m/s)'),
               CLTitem(10.8, 13.7, (74,164,74), 'Liten kuling (10,8-13,7 m/s)'),
               CLTitem(8.0, 10.7, (74,194,134), 'Frisk bris (8-10,7 m/s)'),
               CLTitem(5.5, 7.9, (74,224,194), 'Laber bris (5,5-7,9 m/s)'),
               CLTitem(3.4, 5.4, (74,255,255), 'Lett bris (3,4-5,4 m/s)'),
               CLTitem(1.6, 3.3, (74,194,224), 'Svak vind (1,6-3,3 m/s)'),
               CLTitem(300.1, FloatFillValue, (255, 255, 255), 'Ingen data')]
    
    cltfile = CLT()
    cltfile.new(hdr, cltlist)
    cltfile.write(r"Z:\tmp\wind_10m_daily\avg_wind_speed_10_no.clt")
    
    
def __clt_max_wind_speed_no():
    from pysenorge.io.png import CLT, HDR, CLTitem
    hdr = HDR(255, 8,
              'Maksimal vindhastighet',
              'Maksimal vindhastighet i 10 m h�yde',
              'Vindstyrke')
    # yr.no skala
#    cltlist = [CLTitem(36.7, 300.0, (255,74,74), 'Orkan (over 32,6 m/s)'),
#               CLTitem(28.5, 32.6, (126, 0, 255), 'Sterk storm (28,5-32,6 m/s)'),
#               CLTitem(24.5, 28.4, (255,194,74), 'Full storm (24,5-28,4 m/s)'),
#               CLTitem(20.8, 24.4, (255,255,74), 'Liten storm (20,8-24,4 m/s)'),
#               CLTitem(17.2, 20.7, (194,224,74), 'Sterk kuling (17,2-20,7 m/s)'),
#               CLTitem(13.9, 17.1, (134,194,74), 'Stiv kuling (13,9-17,1 m/s)'),
#               CLTitem(10.8, 13.7, (74,164,74), 'Liten kuling (10,8-13,7 m/s)'),
#               CLTitem(8.0, 10.7, (74,194,134), 'Frisk bris (8-10,7 m/s)'),
#               CLTitem(5.5, 7.9, (74,224,194), 'Laber bris (5,5-7,9 m/s)'),
#               CLTitem(3.4, 5.4, (74,255,255), 'Lett bris (3,4-5,4 m/s)'),
#               CLTitem(1.6, 3.3, (74,194,224), 'Svak vind (1,6-3,3 m/s)'),
#               CLTitem(300.1, FloatFillValue, (255, 255, 255), 'Ingen data')]
    
    cltlist = [CLTitem(36.7, 300.0, (80,0,153), 'Orkan (over 32,6 m/s)'),
               CLTitem(28.5, 32.6, (80,13,243), 'Sterk storm (28,5-32,6 m/s)'),
               CLTitem(24.5, 28.4, (205,13,243), 'Full storm (24,5-28,4 m/s)'),
               CLTitem(20.8, 24.4, (243,13,186), 'Liten storm (20,8-24,4 m/s)'),
               CLTitem(17.2, 20.7, (243,13,76), 'Sterk kuling (17,2-20,7 m/s)'),
               CLTitem(13.9, 17.1, (243,66,13), 'Stiv kuling (13,9-17,1 m/s)'),
               CLTitem(10.8, 13.7, (243,150,13), 'Liten kuling (10,8-13,7 m/s)'),
               CLTitem(8.0, 10.7, (243,234,13), 'Frisk bris (8-10,7 m/s)'),
               CLTitem(5.5, 7.9, (182,243,13), 'Laber bris (5,5-7,9 m/s)'),
               CLTitem(3.4, 5.4, (48,243,13), 'Lett bris (3,4-5,4 m/s)'),
               CLTitem(1.6, 3.3, (13,243,115), 'Svak vind (1,6-3,3 m/s)'),
               CLTitem(0.0, 1.6, (174,174,174), 'Vindstille (<1,6 m/s)'),
               CLTitem(300.1, FloatFillValue, (255, 255, 255), 'Ingen data')]
    
    cltfile = CLT()
    cltfile.new(hdr, cltlist)
    cltfile.write(r"Z:\tmp\wind_10m_daily\max_wind_speed_10_no.clt")

def __clt_bil_max_wind_speed_no():
    from pysenorge.io.png import CLT, HDR, CLTitem
    hdr = HDR(255, 8,
              'Maksimal vindhastighet',
              'Maksimal vindhastighet i 10 m h�yde',
              'Vindstyrke')
    
    cltlist = [CLTitem(367, 3000, (80,0,153), 'Orkan (over 32,6 m/s)'),
               CLTitem(285, 326, (80,13,243), 'Sterk storm (28,5-32,6 m/s)'),
               CLTitem(245, 284, (205,13,243), 'Full storm (24,5-28,4 m/s)'),
               CLTitem(208, 244, (243,13,186), 'Liten storm (20,8-24,4 m/s)'),
               CLTitem(172, 207, (243,13,76), 'Sterk kuling (17,2-20,7 m/s)'),
               CLTitem(139, 171, (243,66,13), 'Stiv kuling (13,9-17,1 m/s)'),
               CLTitem(108, 137, (243,150,13), 'Liten kuling (10,8-13,7 m/s)'),
               CLTitem(80, 107, (243,234,13), 'Frisk bris (8-10,7 m/s)'),
               CLTitem(55, 79, (182,243,13), 'Laber bris (5,5-7,9 m/s)'),
               CLTitem(34, 54, (100,224,121), 'Lett bris (3,4-5,4 m/s)'),
               CLTitem(16, 33, (100,224,187), 'Svak vind (1,6-3,3 m/s)'),
               CLTitem(0, 16, (174,174,174), 'Vindstille (<1,6 m/s)'),
               CLTitem(3001, UintFillValue, (255, 255, 255), 'Ingen data')]
    
    cltfile = CLT()
    cltfile.new(hdr, cltlist)
    cltfile.write(r"Z:\snowsim\wind_speed_max_10m\wind_speed_max_10m_no_bil.clt")

def __clt_wind_direction_no():
    from pysenorge.io.png import CLT, HDR, CLTitem
    hdr = HDR(255, 8,
              'Hovedvindretning',
              'Hovedvindretning i 10 m h�yde',
              'Himmelretning')
    cltlist = [CLTitem(0, 1, (0,0,255), 'N'),
               CLTitem(1, 2, (126, 0, 255), 'N�'),
               CLTitem(2, 3, (255, 0, 215), '�'),
               CLTitem(3, 4, (255, 126, 0), 'S�'),
               CLTitem(4, 5, (255, 0, 0), 'S'),
               CLTitem(5, 6, (255, 245, 0), 'SV'),
               CLTitem(6, 7, (0, 255, 0), 'V'),
               CLTitem(7, 8, (0, 230, 255), 'NV'),
               CLTitem(8, 255, (255, 255, 255), 'Ingen data')]
    
    cltfile = CLT()
    cltfile.new(hdr, cltlist)
    cltfile.write(r"Z:\tmp\wind_10m_daily\wind_direction_10_no.clt")


def __clt_wind_direction_en():
    from pysenorge.io.png import CLT, HDR, CLTitem
    hdr = HDR(255, 8,
              'Prevailing wind direction',
              'Prevailing wind direction at 10 m above ground',
              'Cardinal direction')
    cltlist = [CLTitem(0, 1, (0,0,255), 'N'),
               CLTitem(1, 2, (126, 0, 255), 'NE'),
               CLTitem(2, 3, (255, 0, 215), 'E'),
               CLTitem(3, 4, (255, 126, 0), 'SE'),
               CLTitem(4, 5, (255, 0, 0), 'S'),
               CLTitem(5, 6, (255, 245, 0), 'SW'),
               CLTitem(6, 7, (0, 255, 0), 'W'),
               CLTitem(7, 8, (0, 230, 255), 'NW'),
               CLTitem(8, 255, (255, 255, 255), 'No data')]
    
    cltfile = CLT()
    cltfile.new(hdr, cltlist)
    cltfile.write(r"Z:\tmp\wind_10m_daily\wind_direction_10_en.clt")
    
if __name__ == '__main__':
    main()

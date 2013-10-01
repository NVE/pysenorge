'''
Calculates mean temperature differences between two following days.  

Name
====
    Daily temperature change

Theme information
=================
    The map shows the change in average daily temperature (in C) during previous 24-hour period at 7 a.m. (8 a.m. in summer time) for given date.
    Maps for I{today} and I{tomorrow} are forecasts; earlier maps are based on observations.

Command line usage
==================
    python //~/pysenorge/theme_layers/temperature_gradient_daily.py tm_TODAY.bil tm_YESTERDAY.bil [options]
    

@note: A seNorge temperature day spans from 06:00 UTC to 06:00 UTC the next day. In Norway that corresponds to
08:00 to 08:00 during the summer time and 07:00-07:00 during winter (normal) time.

@todo: Check that days are only one day apart (will depend on filename convention).
@todo: Check that today is later than yesterday (will depend on filename convention).
@todo: Once metadata is available as from netCDF, units can be verified, too.

@author: kmu
@since: 17. aug. 2010

@change: kmu, 20.09.2010, made option --year obsolete
@change: kmu, 2010-10-08, fixed bug in datatype conversion 
@todo: ensure correct netCDF output
@todo: use date2num instead of date2epoch
'''
# Built-in
import os
from optparse import OptionParser

# Adds folder containing the "pysenorge" package to the PYTHONPATH
execfile("set_pysenorge_path.py")

# Additional
from numpy import flipud, arange, int16, float32
try: # for future purpose
    from netCDF4 import date2num #@UnusedImport
except ImportError:
    pass # Error message will be delivered by IO module!
# Own
from pysenorge.set_environment import METdir, BILout, IntFillValue #@UnresolvedImport
from pysenorge.io.bil import BILdata #@UnresolvedImport
from pysenorge.tools.date_converters import get_date_filename #@UnresolvedImport
from pysenorge.converters import int2float, date2epoch #@UnresolvedImport
from pysenorge.grid import senorge_mask #@UnresolvedImport

def model(tm_today, tm_yesterday):
    """
    Main algorithm that produces the theme.
    
    @param tm_today: Mean daily temperature from the latest date.
    @type tm_today: numpy array
    @param tm_yesterday: Mean daily temperature from the day before temp_today.
    @type tm_yesterday: numpy array
     
    @note: Only the model() function is verified in the corresponding unittest - see L{verify.v_temperature_gradient_daily}.
    """
    return tm_today - tm_yesterday


def main():
    '''
    Loads and verifies input data, calls the model, and controls the output stream. 
    '''
    # Theme variables
    themedir = 'tmgr'
    themename = 'Temperature gradient last 24h'

    # Setup input parser
    usage = "usage: python //~HOME/pysenorge/themes/temperature_gradient_daily.py tm_TODAY.bil tm_YESTERDAY.bil [options]"

    parser = OptionParser(usage=usage)
    parser.add_option("-o", "--outdir", 
                      action="store", dest="outdir", type="string",
                      metavar="DIR", default=os.path.join(BILout, themedir),
                      help="Output directory - default: $BILout/%s/$YEAR" % themedir)
    parser.add_option("--no-bil",
                  action="store_false", dest="bil", default=True,
                  help="Set to suppress output in BIL format")
    parser.add_option("--nc",
                  action="store_true", dest="nc", default=False,
                  help="Set to store output in netCDF format")
    parser.add_option("--png",
                  action="store_true", dest="png", default=False,
                  help="Set to store output as PNG image")
    # Comment to suppress help
    parser.print_help()

    (options, args) = parser.parse_args()

    yy, mm, dd = get_date_filename(args[0])
    yy_range = arange(1950, 2050)

    # Verify input parameters
    if int(yy) not in yy_range:
        parser.error("Could not determine year from file name.")

    if len(args) != 2:
        parser.error("Please provide two input files!")
        parser.print_help() 
    else:
        # Add full path to the filename
        todaysfile = os.path.join(METdir, "tm", yy, args[0])
        yesterdaysfile = os.path.join(METdir, "tm", yy, args[1])
        
    
    if not os.path.exists(todaysfile):# and os.path.isfile(options.todaysfile):
        parser.error("BIL file containing todays temperature data does not exist!")
    elif not os.path.exists(yesterdaysfile):# and os.path.isfile(options.todaysfile):
        parser.error("BIL file containing yesterdays temperature data does not exist!")
    else:
        # Load todays data
        today = BILdata(todaysfile, 'uint16')
        today.read()
        # Load yesterdays data 
        yesterday = BILdata(yesterdaysfile, 'uint16')
        yesterday.read()
    
    
    # Setup outputs
    outfile = themedir+'_'+yy+'_'+mm+'_'+dd
    tstring = yy+'-'+mm+'-'+dd+' 06:00:00'
    if options.nc:
        secs = date2epoch(tstring) # used in NCdata.new()
    outdir = os.path.join(options.outdir, yy)
    if not os.path.exists(outdir):
        if not os.path.exists(options.outdir):
            os.chdir(BILout)
            os.system('mkdir %s' % themedir)
        os.chdir(options.outdir)
        os.system('mkdir %s' % yy)
    
    
#    # Calculate temperature gradient    
    tmgr = int16(model(float32(today.data), float32(yesterday.data)))
    
    # Set no-data values to IntFillValue
    mask = senorge_mask()
    imask = mask==False
    tmgr[mask] = IntFillValue
    
    if options.bil:
        # Write to BIL file
        bilfile = BILdata(os.path.join(outdir, outfile+'.bil'), datatype='int16')
        biltext = bilfile.write(tmgr)
        print biltext
    
    if options.nc:
        from pysenorge.io.nc import NCdata #@UnresolvedImport
        # Prepare data
        nctmgr = int2float(tmgr)
        imask = mask == False
        # Convert to Celcius/Kelvin
        nctmgr[imask] = nctmgr[imask]/10.0
        # Change array order 
        nctmgr = flipud(nctmgr)
        # Write to NC file
        ncfile = NCdata(os.path.join(outdir, outfile+'.nc'))
        ncfile.zip = True
        ncfile.new(secs)
        ncfile.add_variable(themedir, nctmgr.dtype.str, "K s-1", themename, nctmgr)
        ncfile.close()
    
    if options.png:
        from pysenorge.io.png import writePNG #@UnresolvedImport
        # Write to PNG file
        writePNG(tmgr, os.path.join(outdir, outfile))
    # At last - cross fingers it all worked out!
    print "\n*** Finished successfully ***\n"
    
if __name__ == "__main__":
    main()

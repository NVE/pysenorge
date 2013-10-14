'''
Calculates mean temperature differences between two following days.

Name
====
    Daily temperature change

Theme information
=================
    The map shows the change in average daily temperature (in C) during
    previous 24-hour period at 7 a.m. (8 a.m. in summer time) for given date.
    Maps for I{today} and I{tomorrow} are forecasts; earlier maps are based
    on observations.

Command line usage
==================
    python //~/pysenorge/theme_layers/temperature_gradient_daily.py [Date]
    [Option]

    It is possible to create either a bil or a netCDF file.

@note: A seNorge temperature day spans from 06:00 UTC to 06:00 UTC
the next day. In Norway that corresponds to 08:00 to 08:00 during the summer time and
07:00-07:00 during winter (normal) time.

@todo: Once metadata is available as from netCDF,
units can be verified, too.

@author: kmu
@since: 17. aug. 2010

@change: kmu, 20.09.2010, made option --year obsolete
@change: kmu, 2010-10-08, fixed bug in datatype conversion
@change: RL, 2013-10-01, changed to lite-weight server version with
         less options and a more consistently ussage in relation to
         other scripts from pysenorge.
@todo: ensure corect netCDF output
@todo: use date2num instead of date2epoch
'''

# Built-in
import os
import datetime
from optparse import OptionParser

# Adds folder containing the "pysenorge" package to the PYTHONPATH
execfile("set_pysenorge_path.py")

# Additional
from numpy import flipud, int16, float32

# Own
from pysenorge.set_environment import METdir, BILout, IntFillValue
from pysenorge.io.bil import BILdata
from pysenorge.tools.date_converters import iso2datetime, get_hydroyear
from pysenorge.converters import int2float, date2epoch
from pysenorge.grid import senorge_mask


def model(tm_today, tm_yesterday):
    """
    Main algorithm that produces the theme.

    @param tm_today: Mean daily temperature from the latest date.
    @type tm_today: numpy array
    @param tm_yesterday: Mean daily temperature from the day before temp_today.
    @type tm_yesterday: numpy array

    @note: Only the model() function is verified in the corresponding unittest
    - see L{verify.v_temperature_gradient_daily}.
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
    usage = "usage: python //~HOME/pysenorge/themes/temperature_gradient \
    [Date] [Option]"

    parser = OptionParser(usage=usage)
    parser.add_option("--no-bil",
                  action="store_false", dest="bil", default=True,
                  help="Set to suppress output in BIL format")
    parser.add_option("--nc",
                  action="store_true", dest="nc", default=False,
                  help="Set to store output in netCDF format")

    # Comment to suppress help
    parser.print_help()

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("Please provide two input files!")
        parser.print_help()

    #Select which date
    yr = str(args[0].split("-")[0])
    mon = str(args[0].split("-")[1])
    day = str(args[0].split("-")[2])

    load_date = "%s_%s_%s" % (yr, mon, day)
    yesterday = (datetime.date(int(yr), int(mon), int(day)) -
                datetime.timedelta(days=1)).strftime("%Y_%m_%d")

    cdt = iso2datetime(args[0] + " 06:00:00")

    todayfile = "tm_%s.bil" % load_date
    yesterdayfile = "tm_%s.bil" % yesterday
    file_path = os.path.join(METdir, "tm", str(get_hydroyear(cdt)))

    # Import of tmfile from yesterday and today
    if not os.path.exists(os.path.join(file_path, todayfile)):
        print "tm file from today doesn't exist or path is not correct"
    elif not os.path.exists(os.path.join(file_path, todayfile)):
        print "tm file from yesterday doesn't exist or path is not correct"
    else:
        # Import todays data
        today = BILdata(os.path.join(file_path, todayfile), 'uint16')
        today.read()
        # Import yesterdays data
        ob_yesterday = BILdata(os.path.join(file_path, yesterdayfile), 'uint16')
        ob_yesterday.read()

    # Calculate temperature gradient
    tmgr = int16(model(float32(today.data), float32(ob_yesterday.data)))

    # Set no-data values to IntFillValue
    mask = senorge_mask()
    imask = mask == False
    tmgr[mask] = IntFillValue

    # Setup outputs
    outfile = themedir + '_' + load_date + ".bil"
    outdir = os.path.join(BILout, themedir, str(get_hydroyear(cdt)))

    if not os.path.exists(outdir):
        if not os.path.exists(os.path.join(BILout, themedir)):
            os.chdir(BILout)
            os.makedirs(themedir)
        os.chdir(os.path.join(BILout, themedir))
        os.makedirs(str(get_hydroyear(cdt)))

    if options.bil:
        # Write to BIL file
        bilfile = BILdata(os.path.join(outdir, outfile), datatype='int16')
        biltext = bilfile.write(tmgr * 10)
        print biltext

    if options.nc:
        from pysenorge.io.nc import NCdata
        # Prepare data
        nctmgr = int2float(tmgr)
        imask = mask == False
        # Convert to Celcius/Kelvin
        nctmgr[imask] = nctmgr[imask] / 10.0
        # Change array order
        nctmgr = flipud(nctmgr)
        # Write to NC file
        ncfile = NCdata(os.path.join(outdir, outfile + '.nc'))
        ncfile.zip = True
        secs = date2epoch(cdt)
        ncfile.new(secs)
        ncfile.add_variable(themedir, nctmgr.dtype.str,
                            "K s-1", themename, nctmgr)
        ncfile.close()

    print "\n*** Finished successfully ***\n"

if __name__ == "__main__":
    main()

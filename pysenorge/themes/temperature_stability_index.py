# -*- coding:UTF-8 -*-
'''
Shows potential changes in snow stability based on temperature and
temperature gradient history.

@author: kmu
@since: 4. oct. 2010
@updated by RL 11. sep. 2013
'''
# Built-in
import os
from optparse import OptionParser

# Additional
from numpy import zeros, uint16, float32

# Own
execfile("set_pysenorge_path.py")  # Adds folder containing the "pysenorge" package to the PYTHONPATH @UnusedImport
from pysenorge.set_environment import METdir, BILout, UintFillValue
from pysenorge.io.bil import BILdata
from pysenorge.grid import senorge_mask
from pysenorge.tools.date_converters import get_hydroyear
from pysenorge.tools.date_converters import iso2datetime


def model(tm, tmgr, nodata_mask):
    '''
    Main algorithm that produces the theme.

    Categories
    ==========
        - Indicator for unchanged stability: -2 C < tmgr < +2 C og tm < -5 C
        - Indicator for increasing stability: tmgr < -5 C og tm > -2 C
        - Indicator for decreasing stability: tmgr > +5 C og tm > -10 C
        - Not categorized: Else

    @param tm: Daily mean air temperature
    @type tm: array of 4-byte floats
    @param tmgr: Temperature gradient between yesterdays and today mean air temperature
    @type tmgr: array of 4-byte floats
    @param nodata_mask: True for nodata values
    @type nodata_mask: bool

    @note: Only the model() function is verified in the corresponding unittest.

    ussage = python temperature_stability_index [Date]
    [Date] = YYYY-MM-DD

    '''
    ssttm = zeros(tmgr.shape, dtype=uint16)
    dims = tmgr.shape
    print tmgr.shape
    for i in xrange(dims[0]):
        for j in xrange(dims[1]):
            if nodata_mask[i][j] == False:  # only consider values that contain data
                if tm[i][j] < -5.0 and tmgr[i][j] > -2.0 and tmgr[i][j] < 2.0:
                    ssttm[i][j] = 1  # unchanged stability
                elif tm[i][j] > -2.0 and tmgr[i][j] < -5.0:
                    ssttm[i][j] = 2  # increased stability
                elif tm[i][j] < -2.0 and tmgr[i][j] > 5.0:
                    ssttm[i][j] = 3  # decreased stability
                    print tmgr[i][j]
                elif tm[i][j] < -2.0 and tmgr[i][j] > 10.0:
                    ssttm[i][j] = 4  # drastically decreased stability
                else:
                    ssttm[i][j] = 0
    return ssttm


def main():
    '''
    Loads and verifies input data, calls the model,
    and controls the output stream.
    '''
    # Theme variables
    themedir = 'ssttm'

    # Setup input parser
    usage = "usage: python //~HOME/pysenorge/themes/temperature_stability_index.py [Date]"

    #Add options
    parser = OptionParser(usage=usage)
    parser.add_option("--no-bil",
                  action="store_false", dest="bil", default=True,
                  help="Set to suppress output in BIL format")

    # Comment to suppress help
    #    parser.print_help()
    (options, args) = parser.parse_args()

    # Verify input parameters

    if len(args) != 1:
        parser.error("Please provide a date YYYY-MM-DD")
    else:
        ob_date = args[0].split("-")
        dd = ob_date[2]
        mm = ob_date[1]
        yy = ob_date[0]
        load_date = "%s_%s_%s" % (yy, mm, dd)
        cdt = iso2datetime(args[0] + " 06:00:00")

    # Import the tm-file and tmgr-file
    tm_file = "tm_%s.bil" % load_date
    tm_path = os.path.join(METdir, "tm", yy, tm_file)

    tmgr_file = "tmgr_%s.bil" % load_date
    tmgr_path = os.path.join(BILout, "tmgr", str(get_hydroyear(cdt)),
                             tmgr_file)

    if os.path.exists(tm_path):
        tm = BILdata(tm_path, datatype='int16')
        tm.read()
    else:
        print "Cannot import tm-file"

    # Load tm data
    if os.path.exists(tmgr_path):
        tmgr = BILdata(tmgr_path, datatype='int16')
        tmgr.read()
    else:
        print "Cannot import tmgr-file"

    # Convert tm to Celsius
    ftm = ((float32(tm.data) - 2731) * 0.1)
    mask = senorge_mask()

    # Convert tmgr to Celsius
    ftmgr = float32(tmgr.data) * 0.1

    # Apply model
    ssttm = model(ftm, ftmgr, mask)
    ssttm[mask] = UintFillValue

    # Set output
    outfile = themedir + '_' + load_date + ".bil"
    outdir = os.path.join(BILout, themedir, str(get_hydroyear(cdt)),
                          outfile)
    if not os.path.exists(os.path.join(BILout, themedir,
                                       str(get_hydroyear(cdt)))):
        if not os.path.exists(os.path.join(BILout, themedir,)):
            os.chdir(BILout)
            os.makedirs(themedir)
        os.chdir(os.path.join(BILout, themedir))
        os.makedirs(str(get_hydroyear(cdt)))

    # Write to BIL file
    bilfile = BILdata(outdir, datatype="uint16")
    biltext = bilfile.write(ssttm)
    print biltext

    # At last - cross fingers it all worked out!
    print "\n*** Finished successfully ***\n"


def _clt_tsi():
    '''
    Creates CLT file for temperature-stability index bil file.
    '''

    from pysenorge.io.png import CLT, HDR, CLTitem
    hdr = HDR(255, 8,
              'Temperatur-stability index',
              '',
              'Snowstability index')
    cltlist = [CLTitem(-0.5, 0.5, (211, 211, 211), 'not classified'),
               CLTitem(0.5, 1.5, (64, 224, 208), 'unchanged'),
               CLTitem(1.5, 2.5, (255, 99, 71), 'increase'),
               CLTitem(2.5, 3.5, (50, 205, 50), 'decrease'),
               CLTitem(3.5, 4.5, (255, 0, 0), 'drastic decrease')]
    cltfile = CLT()
    cltfile.new(hdr, cltlist)
    cltfile.write("CLT_temperature_stability_index.clt")
    print 'Created CLT file for temperature-stability index'

if __name__ == "__main__":
    main()

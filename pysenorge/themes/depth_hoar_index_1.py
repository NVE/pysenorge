# -*- coding:iso-8859-10 -*-
__docformat__ = 'reStructuredText'
'''
Akkumulert temperaturgradient i snødekket (indikatorkart)

    *Menynavn:* Begerkrystallindeks 1
    
    *Tittel på kart:* Akkumulerte temperaturgradienter
     
    *Temaforklaring:* Kartet viser en indeks som angir sannsynligheten for at\
    temperaturforskjeller mellom snøoverflaten og bakken virker\
    destabiliserende på snøpakken. Dannelsen av store krystaller med lav\
    fasthet skjer ved at vanndamp i bunnen av snødekket avsettes på\
    overliggende krystaller. Prosessen går raskere jo større den negative\
    tempearturgradienten er, og svake bunnsjikt kan vedvare gjennom hele\
    vinteren. Indeksen beregnes fra snødybden er minimum 25 cm og nullstilles\
    når snøen forsvinner. Snøpakken antas å være minst stabil når indeksen har\
    store negative verdier. 
 
*Todo:*
- extend color scale from 0-1000 to 0-2000 in external .clt file

*Note:*
- Replace netCDFout by BILout for operational use!

:Author: kmu
:Created: 22. nov. 2010
:updated by Ralf Loritz
'''
# Built-in
import os
import datetime
from optparse import OptionParser

# Adds folder containing the "pysenorge" package to the PYTHONPATH
execfile(os.path.join(os.path.dirname(__file__), "set_pysenorge_path.py"))

# Additional
from numpy import flipud, zeros_like, int16, float32
try: # for future purpose
    from netCDF4 import date2num
except ImportError:
    pass # Error message will be delivered by IO module!
# Own
from pysenorge.set_environment import METdir, PROGdir, BILout, \
                                        IntFillValue
from pysenorge.io.bil import BILdata
from pysenorge.tools.date_converters import datetime2BILdate, iso2datetime,\
                                            get_hydroyear
from pysenorge.grid import senorge_mask


def __model(tm, sd, tgss):
    """
    The map indicates the probability of destabilizing the snow cover
    due to temperature differences between the snow surface and the ground. Large, faceted 
    crystals with weak bounding grow if high temperature gradients are present.
    Water vapor from the warmer surfaces is deposited over colder surfaces.
    The growth rate increases with increasing temperature differences. The resulting weak
    layer might be preserved for the whole season.
    The index is calculated for snow depth >25 cm and resets when the snow is melted
    completely. The snow cover is expected to be weakest when the index map show large,
    negative values.

    :Parameters:
        - tm: Avg. daily air-temperature (seNorge)
        - sd: Snow-depth (seNorge)
        - tgss: Yesterdays temperature-gradient inside the snowpack (this)
    """

    tmdims = tm.shape
    sddims = sd.shape
    if tmdims != sddims:
        print "Temperature grid and snow-depth grid have different shapes!"
    if tgss == None:
        tgss = zeros_like(tm)

    # define flags
    nosnow_flag = 1002.0
    littlesnow_flag = 999.0

    # define masks
    nosnow = sd <= 0.001  # mask for no snow
    littlesnow = sd < 0.25  # mask for thin snow cover
    enoughsnow = sd >= 0.25  # mask for sufficient snow depth
    littletgss = tgss == littlesnow_flag  # mask where tgss is flagged
    inittgss = enoughsnow * littletgss  # mask to init tgss

    # calculate snow temperature gradient (stgr) where sufficient snow is present 
    stgr = zeros_like(tm)
    stgr[enoughsnow] = tm[enoughsnow] / sd[enoughsnow]

    """ Order is important !!! """
    # Set littlesnow_flag first - then nosnow_flag
    tgss += stgr
    tgss[inittgss] = stgr[inittgss]
    tgss[littlesnow] = littlesnow_flag
    tgss[nosnow] = nosnow_flag

    return int16(tgss)

def main():
    '''
    Loads and verifies input data, calls the model, and controls the output stream. 

    Command line usage::

        python //~HOME/pysenorge/themes/depth_hoar_index_1.py YYYY-MM-DD [options]
    '''
    # Theme variables
    themedir = 'depth_hoar_index_1'

    # Setup input parser
    usage = "usage: python //~HOME/pysenorge/themes/depth_hoar_index_1.py YYYY-MM-DD [options]"

    parser = OptionParser(usage=usage)
    parser.add_option("--no-bil",
                  action="store_false", dest="bil", default=True,
                  help="Set to suppress output in BIL format")

    # Comment to suppress help
    parser.print_help()

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("Please provide the date in ISO format YYYY-MM-DD!")
        parser.print_help()

    yr = str(args[0].split("-")[0])
    mon = str(args[0].split("-")[1])
    day = str(args[0].split("-")[2])

    #create a date variable out of input
    load_date = "%s_%s_%s" % (yr, mon, day)
    yesterday = (datetime.date(int(yr), int(mon), int(day)) -
                datetime.datetime.timedelta(days=1)).strftime("%Y_%m_%d")

    cdt = iso2datetime(args[0] + " 06:00:00")

    # Load_path tm bil file
    tmfilename = "tm_%s.bil" % load_date
    tmfile = os.path.join(METdir, "tm", str(cdt.year), tmfilename)
    # Load_path sd bil file
    sdfilename = "sd_%s.bil" % load_date
    sdfile = os.path.join(METdir, "sd", str(get_hydroyear(cdt)), sdfilename)
    # Load_path yesterdays depth hoar index file
    tgssfilename = "%s_%s.bil" % (themedir, yesterday)
    tgssfile = os.path.join(BILout, themedir, str(get_hydroyear(cdt)),
                            tgssfilename)

    # Test if the paths exist
    if not os.path.exists(tmfile):
        tmfile = os.path.join(PROGdir, str(cdt.year), tmfilename)
        print "Warning: Observation not found - using prognosis instead!"

    if not os.path.exists(tmfile):
        parser.error("BIL file containing temperature data does not exist!" %\
                     tmfile)
    elif not os.path.exists(sdfile):
        parser.error("BIL file %s containing snow-depth data does not exist!" %\
                     sdfile)
    else:
        # Load todays data
        tm = BILdata(tmfile, 'uint16')
        tm.read()
        # convert to Celsius
        tm.data = (float32(tm.data) / 10.0) - 273.1
        # Load yesterdays data 
        sd = BILdata(sdfile, 'uint16')
        sd.read()
        # convert mm to m 
        sd.data = float32(sd.data) / 1000.0

    if not os.path.exists(tgssfile):
        print "Yesterdays TGSS data does not exist - using None!"
        tgss = BILdata("tgssdummy", 'int16')
    else:
        # Load todays data
        tgss = BILdata(tgssfile, 'int16')
        tgss.read()
        tgss.data = float32(tgss.data)

    # Setup outputs
    outfile = themedir + '_' + load_date

    outdir = os.path.join(BILin, "depth_hoar_index_1", str(get_hydroyear(cdt)))

    if not os.path.exists(outdir):
        if not os.path.exists(options.outdir):
            os.chdir(BILout)
            os.system('mkdir %s' % themedir)
        os.chdir(options.outdir)
        os.system('mkdir %s' % str(get_hydroyear(cdt)))

    # Calculate sum of snow temperature gradients
    tgss = __model(tm.data, sd.data, tgss.data)
    # Set no-data values to IntFillValue
    mask = senorge_mask()
    tgss[mask] = IntFillValue

    if options.bil:
        # Write to BIL file
        bilfile = BILdata(os.path.join(outdir,
                          outfile + '.bil'),
                          datatype='int16')
        biltext = bilfile.write(tgss)
        print biltext

    # At last - cross fingers it all worked out!
    print "\n*** Finished successfully ***\n"

if __name__ == '__main__':
    main()

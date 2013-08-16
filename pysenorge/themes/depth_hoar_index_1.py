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
'''
# Built-in
import os
from optparse import OptionParser
from datetime import timedelta
# Adds folder containing the "pysenorge" package to the PYTHONPATH
execfile(os.path.join(os.path.dirname(__file__), "set_pysenorge_path.py"))

# Additional
from numpy import flipud, zeros_like, int16, float32
try: # for future purpose
    from netCDF4 import date2num
except ImportError:
    pass # Error message will be delivered by IO module!
# Own
from pysenorge.set_environment import METdir, PROGdir, BILin, BILout, \
                                        IntFillValue, timeunit
from pysenorge.io.bil import BILdata
from pysenorge.tools.date_converters import datetime2BILdate, iso2datetime,\
                                            get_hydroyear
from pysenorge.grid import senorge_mask


def model(tm, sd, tgss):
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
    for i in range(tmdims[0]):
        for j in range(tmdims[1]):
            if sd[i][j] <= 0.0:
                tgss[i][j] = 1002.0 # "no snow" flag
            elif sd[i][j] > 0.0 and sd[i][j] < 0.25:
                if tgss[i][j] >= 999.0:
                    tgss[i][j] = 999.0 # "too little snow" flag               
            elif sd[i][j] >= 0.25 and tgss[i][j] >= 999.0:
                tgss[i][j] = (tm[i][j]/sd[i][j]) # init when snow is thick enough
            else:
                tgss[i][j] += (tm[i][j]/sd[i][j])

    return tgss

def __model(tm, sd, tgss):
    """
    
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
    nosnow = sd <= 0.001 # mask for no snow
    littlesnow = sd < 0.25 # mask for thin snow cover
    enoughsnow = sd >= 0.25 # mask for sufficient snow depth
    littletgss = tgss == littlesnow_flag # mask where tgss is flagged
    inittgss = enoughsnow * littletgss # mask to init tgss
    
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
    themename = 'Depth hoar index 1'
    
    # Setup input parser
    usage = "usage: python //~HOME/pysenorge/themes/depth_hoar_index_1.py YYYY-MM-DD [options]"
    
    parser = OptionParser(usage=usage)
    parser.add_option("-o", "--outdir", 
                      action="store", dest="outdir", type="string",
                      metavar="DIR", default=os.path.join(BILout, themedir),
                      help="Output directory - default: $BILout/%s/$HYDROYEAR" % \
                      themedir)
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
    
    if len(args) != 1:
        parser.error("Please provide the date in ISO format YYYY-MM-DD!")
        parser.print_help() 
    
    # get current datetime
    cdt = iso2datetime(args[0]+" 06:00:00")
    oneday = timedelta(days=1)
    tmfilename = "tm_%s.bil" % datetime2BILdate(cdt)
    sdfilename = "sd_%s.bil" % datetime2BILdate(cdt)
    # yesterdays tgss data file
    tgssfilename = "%s_%s.bil" % (themedir, datetime2BILdate(cdt-oneday))
    
    # Add full path to the filename
    tmfile = os.path.join(METdir, "tm", str(cdt.year), tmfilename)
    sdfile = os.path.join(BILin, "sd", str(get_hydroyear(cdt)), sdfilename)
    tgssfile = os.path.join(BILout, themedir, str(get_hydroyear(cdt-oneday)),
                            tgssfilename)
    
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
    outfile = themedir+'_'+datetime2BILdate(cdt)
    if options.nc:
        secs = date2num(cdt, timeunit) # used in NCdata.new()
    outdir = os.path.join(options.outdir, str(get_hydroyear(cdt)))
    if not os.path.exists(outdir):
        if not os.path.exists(options.outdir):
            os.chdir(BILout)
            os.system('mkdir %s' % themedir)
        os.chdir(options.outdir)
        os.system('mkdir %s' % str(get_hydroyear(cdt)))
        
    # Calculate sum of snow temperature gradients    
#    tgss = int16(model(tm.data, sd.data, tgss.data))
    tgss = __model(tm.data, sd.data, tgss.data)
    # Set no-data values to IntFillValue
    mask = senorge_mask()
    tgss[mask] = IntFillValue
    
    if options.bil:
        # Write to BIL file
        bilfile = BILdata(os.path.join(outdir, outfile+'.bil'),
                          datatype='int16')
        biltext = bilfile.write(tgss)
        print biltext
    
    if options.nc:
        from pysenorge.io.nc import NCdata
        # Prepare data
        # Change array order 
        nctgss = flipud(tgss)
        # Write to NC file
        ncfile = NCdata(os.path.join(outdir, outfile+'.nc'))
        ncfile.zip = True
        ncfile.new(secs)
        ncfile.add_variable(themedir, nctgss.dtype.str, "K m-1 per day",
                            themename, nctgss)
        ncfile.close()
    
    if options.png:
        from pysenorge.io.png import writePNG
        # Write to PNG file
        writePNG(flipud(tgss), os.path.join(outdir, outfile),
                 cltfile=os.path.join(BILout, themedir, "tgss.clt")
                 )
        
    # At last - cross fingers it all worked out!
    print "\n*** Finished successfully ***\n"
    
    
import unittest

class TestModel(unittest.TestCase):

    def test_required_depth(self):
        from numpy import asarray
        
        sd = asarray([[50., 0.], [25., 10.]])
        tm = asarray([[-25., -25.], [-25., -25.]])
        tgss = asarray([[-0.5, 1002], [-1.0, -2.5]])
        result = model(tm, sd, None)
        for i in range(2):
            for j in range(2):
                self.assertEqual(result[i][j], tgss[i][j])




    

if __name__ == '__main__':
    main()
#    unittest.main()
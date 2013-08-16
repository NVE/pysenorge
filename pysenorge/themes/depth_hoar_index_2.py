#! /usr/bin/python
# -*- coding:iso-8859-10 -*-
__docformat__ = 'reStructuredText'
'''
Antall dager med oppbyggende omvandling i snødekket (indikatorkart)

    B{Menynavn:} Rennsn�indeks 2
    
    B{Tittel på kart:} Rennsn�indeks 2 - Dager med begerkrystalldannelse
     
    B{Temaforklaring:} Kartet viser en indeks som angir antall dager med stor
    sannsynlighet for begerkrystalldannelse. Når temperaturgradienten i snødkket
    overskrider -10 C/m er det sannsynlig at det dannes begerkrystaller virker 
    destabiliserende i bunnen av snødekket som. Indeksen beregnes fra snødybden
    er minimum 25 cm og nullstilles når snøen forsvinner. Snøpakken antas å være
    minst stabil når indeksen har et høyt antall dager.   


:Author: kmu
:Created: 22. nov. 2010

:ToDo:
- path to .clt file is hardcoded
- add a clause that resets the day-counter after an extended period with mild
    temperatures

'''
# Built-in
import os
from optparse import OptionParser
from datetime import timedelta
# Adds folder containing the "pysenorge" package to the PYTHONPATH
execfile(os.path.join(os.path.dirname(__file__), "set_pysenorge_path.py"))

# Additional
from numpy import flipud, zeros_like, uint16, float32, asarray
try: # for future purpose
    from netCDF4 import date2num
except ImportError:
    pass # Error message will be delivered by IO module!
# Own
from pysenorge.set_environment import METdir, PROGdir, BILin, BILout, \
                                        UintFillValue, timeunit
from pysenorge.io.bil import BILdata
from pysenorge.tools.date_converters import datetime2BILdate, iso2datetime,\
                                            get_hydroyear
from pysenorge.grid import senorge_mask


def model(tm, sd, tds):
    """
    Doc...
    
    :Parameters:
        - tm: Todays daily average temperature (seNorge)
        - sd: Todays snow depth (seNorge)
        - tds: Yesterdays depth hoar index (this)
    """
    
    littlesnow_flag = 65533
    nosnow_flag = 65534
    
    if tds == None: # init tds if not existent
        tds = uint16(zeros_like(tm))
    
    # define the array masks
    nosnow = sd <= 0.001 # mask for no snow
    littlesnow = sd < 0.25 # mask for thin snow cover
    enoughsnow = sd >= 0.25 # mask for sufficient snow depth
    
    # calculate snow temperature gradient (stgr) where sufficient snow is present 
    stgr = zeros_like(tm)
    stgr[enoughsnow] = tm[enoughsnow] / sd[enoughsnow]
    
    # define further array masks
    largegradient = stgr <= -10.0 # mask for large neg. temperature gradients
    increasetds = enoughsnow * largegradient # mask where to increase tds
    littletds = tds == littlesnow_flag # mask where tds is flagged
    inittds = enoughsnow * littletds # mask to init tds with 1 day
    
    """ Order is important !!! """
    # Set littlesnow_flag first - then nosnow_flag 
    tds[inittds] = 0
    tds[increasetds] = tds[increasetds] + 1
    tds[littlesnow] = littlesnow_flag
    tds[nosnow] = nosnow_flag
    
    return tds 
    

def main():
    '''
    Loads and verifies input data, calls the model, and controls the output stream. 
    
    Command line usage::
    
        python //~HOME/pysenorge/themes/temperature_destabilization.py YYYY-MM-DD [options]
    '''
    # Theme variables
    themedir = 'depth_hoar_index_2'
    themename = 'Depth hoar index 2'
    
    # Setup input parser
    usage = "usage: python //~HOME/pysenorge/themes/temperature_destabilization.py YYYY-MM-DD [options]"
    
    parser = OptionParser(usage=usage)
    parser.add_option("-o", "--outdir", 
                      action="store", dest="outdir", type="string",
                      metavar="DIR", default=os.path.join(BILout, themedir),
                      help="Output directory - default: $BILout/%s/$HYDROYEAR" % themedir)
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
    # yesterdays tds data file
    tdsfilename = "%s_%s.bil" % (themedir, datetime2BILdate(cdt-oneday))
    
    # Add full path to the filename
    tmfile = os.path.join(METdir, "tm", str(cdt.year), tmfilename)
    sdfile = os.path.join(BILin, "sd", str(get_hydroyear(cdt)), sdfilename)
    tdsfile = os.path.join(BILout, themedir, str(get_hydroyear(cdt-oneday)),
                            tdsfilename)
    
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
        
    if not os.path.exists(tdsfile):
        print "Yesterdays TDS2 data does not exist - using None!"
        tds = BILdata("tdsdummy", 'uint16')
    else:
        # Load todays data
        tds = BILdata(tdsfile, 'uint16')
        tds.read()
#        tds.data = float32(tds.data)
        
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
#    tds = uint16(model(tm.data, sd.data, tds.data))
    tds = model(tm.data, sd.data, tds.data)
        
    # Set no-data values to UintFillValue
    mask = senorge_mask()
    tds[mask] = UintFillValue    
    
    if options.bil:
        # Write to BIL file
        bilfile = BILdata(os.path.join(outdir, outfile+'.bil'),
                          datatype='uint16')
        biltext = bilfile.write(tds)
        print biltext
    
    if options.nc:
        from pysenorge.io.nc import NCdata
        # Prepare data
#        nctds = int2float(tds)
#        imask = mask == False
#        # Convert to Celcius/Kelvin
#        nctds[imask] = nctds[imask]/10.0
        # Change array order 
        nctds = flipud(tds)
        # Write to NC file
        ncfile = NCdata(os.path.join(outdir, outfile+'.nc'))
        ncfile.zip = True
        ncfile.new(secs)
        ncfile.add_variable(themedir, nctds.dtype.str, "days",
                            themename, nctds)
        ncfile.close()
    
    if options.png:
        from pysenorge.io.png import writePNG
        # Write to PNG file
        writePNG(flipud(tds), os.path.join(outdir, outfile),
                 cltfile=r"Z:\snowsim\%s\tgss2_v2.clt" % themedir
                 )
        
    # At last - cross fingers it all worked out!
    print "\n*** Finished successfully ***\n"

def __test():
    tm = asarray([[2, -5],
                  [-10, -15]], float32)
    
    sd = asarray([[0, 0.20],
                  [0.25, 0.50]], float32)
    
    tm2 = asarray([[2, -12],
                  [-10, -15]], float32)
    
    sd2 = asarray([[0, 0.27],
                  [0.25, 0.50]], float32)
    
#    tds = asarray([[0, 0],
#                  [0, 0]], uint16)
    
    tds = None
    
    tds = model(tm, sd, tds)
    print tds
    
    tds = model(tm2, sd2, tds)
    print tds
    
    tds = model(tm, sd, tds)
    print tds
    


if __name__ == '__main__':
#    __test()
    main()
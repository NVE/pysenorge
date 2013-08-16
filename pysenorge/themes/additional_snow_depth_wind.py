__docformat__ = 'reStructuredText'
'''
Wind-transported snow

:Author: kmu
:Created: 11. may 2011

'''
# Built-in
import os
from optparse import OptionParser

# Adds folder containing the "pysenorge" package to the PYTHONPATH
execfile(os.path.join(os.path.dirname(__file__), "set_pysenorge_path.py"))

# Additional
from numpy import flipud, float32, zeros_like, uint16, clip
# Own
from pysenorge.set_environment import BILout, UintFillValue
from pysenorge.tools.date_converters import datetime2BILdate, iso2datetime,\
                                            get_hydroyear
#from pysenorge.functions.snow_transport import AdditionalSnowDepth,\
#                                              WindThresholdLi
from pysenorge.io.bil import BILdata
from pysenorge.grid import senorge_mask


def __model(u, nsd):
    '''  
    :Parameters:
        - u: average daily wind speed [m/s] (UM4->seNorge)
        - nsd: new snow depth [mm] (this)
    '''
    
    Hwind = zeros_like(u)
    a1 = nsd > 50 # ignore new snow depth below 5 cm
    a2 = nsd < 65531 
    a = a1*a2 # mask that excludes cells without new snow and special markers
    uc = clip(u, 0, 20) # set wind speeds >20 m s-1 to 20 m s-1 - disregards the fact the higher wind speeds actually lead to weaker snow transport due to increased sublimation.
    k = 8e-5 # [s3 d-1 m-2]
    Hwind[a] = k * uc[a]**3 # additional snow depth after Foehn(1980)

    return Hwind

def model(u, nsd, lwc, age):
    '''    
    Empirical formulation relating the additional snow depth |Hwind| deposited in lee
    slopes per day to the third power of the daily average wind speed u
    (u<=20 m |s-1|). The model is only valid for blowing snow. For each new snow event
    the additional loading in lee slopes is calculated. Snow drift of already
    deposited snow is not taken into account at the moment.
    
    The threshold wind speed (|Ut|) depends on the friction between the snow surface and
    air. Li & Pomeroy (1997) proposed an empirical relationship based on 2 m air
    temperature. They found minimum threshold wind speeds of 4 m |s-1| for dry snow 
    and a 7 m |s-1| for wet snow over the Canadian praire.  
    
    Only the hours of wind speeds above |Ut| should be considered. The hours the
    wind speed is larger than |Ut| and the time since the last snowfall need to be
    considered since they substantially influence the amount of snow that is 
    available for transport.
    Short periods of high wind speeds shortly after snow fall will transport more 
    snow than calm winds over old, well settled snow. 
    
    **References:**
        - Foehn, P. M. B. (1980). Snow transport over mountain crests. Journal of Glaciology, 26(94).
        - Meister, R., Influence of strong winds on snow distribution and avalanche activity, Ann. Glac., 13, pp.195-201, 1989 
        - Schweizer, J. (2003). Snow avalanche formation. Reviews of Geophysics, 41(4)
    
    **ToDo:**
        - Use LWC<3> to separate threshold values 4 and 7 m |s-1|
        - High LWC and refreezing needs to be remembered until next snowfall. No snow transport after refreezing! Use a .npy file to store if refrozen snow has been covered by new snow again.
        
    **Done:**
        - Differentiate between blowing and drifting snow: Blowing snow only under snow fall.
        - Snow drift peaks at 20 m |s-1| and decreases with even higher wind speeds due to saturation (Doorshot et al., 2001)
    
    :Parameters:
        - u: average daily wind speed [m |s-1|] (UM4->seNorge)
        - nsd: new snow depth [mm] (seNorge)
        - lwc: liquid water content % (0-3% dry, 3-9% moist, >9% wet) (seNorge)
        - age: days since last snow fall (seNorge)
        
    .. |Hwind| replace:: H\ :sub:`wind`
    .. |s-1| replace:: s\ :sup:`-1`
    .. |Ut| replace:: U\ :sub:`t`
    '''
    age_new = age < 2 # fresh snow, same transport as under snow fall
    age_old = age >= 2 # older snow, transport depends on LWC
    
    lwc_dry= lwc < 3
    lwc3 = lwc >= 3
    lwc9 = lwc < 9
    lwc_moist = lwc3*lwc9 # moist snow, reduced wind transport
#    lwc9 = lwc >= 9
#    lwc251 = lwc < 251
#    lwc_wet = lwc9*lwc251 # wet snow, no wind transport
    
    Hwind = zeros_like(u) # init array
    uc = clip(u, 0, 20) # set wind speeds >20 m s-1 to 20 m s-1 - disregards the fact the higher wind speeds actually lead to weaker snow transport due to increased sublimation.
    k = 8e-5 # [s3 d-1 m-2]
    
    mask = age_new*lwc_dry
    Hwind[mask] = k * uc[mask]**3 # additional snow depth after Foehn(1980)
    
    mask = age_new*lwc_moist # reduced transport for moist, new snow
    Hwind[mask] = k * (uc[mask]-7.0)**3 # set threshold wind speed to 7 m/s
    
    mask = age_old*lwc_dry # reduced transport for dry, old snow
    Hwind[mask] = k * (uc[mask]-4.0)**3 # set threshold wind speed to 4 m/s
    
    # No transport when snow is wet or old and moist    
    
    return Hwind

def main():
    '''
    Loads and verifies input data, calls the model, and controls the output stream. 
    
    Command line usage::
    
        python //~HOME/pysenorge/themes/additional_snow_depth_wind.py YYYY-MM-DD [options]
    '''
    # Theme variables
    themedir = 'additional_snow_depth'
    themename = ''
    
    # Setup input parser
    usage = "usage: python //~HOME/pysenorge/themes/additional_snow_depth.py YYYY-MM-DD [options]"
    
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
#    parser.print_help()

    (options, args) = parser.parse_args()
    
    if len(args) != 1:
        parser.error("Please provide the date in ISO format YYYY-MM-DD!")
        parser.print_help() 
    
    # get current datetime
    cdt = iso2datetime(args[0]+" 06:00:00")
    windfilename = "wind_speed_avg_600m_%s.bil" % datetime2BILdate(cdt)
    
    # Add full path to the filename
    windfile = os.path.join(BILout, "wind_speed_avg_600m", str(get_hydroyear(cdt)),
                            windfilename)
    if not os.path.exists(windfile):
        parser.error("BIL file %s containing wind data does not exist!" %\
                     windfile)
    else:
        # Load todays data
        wind = BILdata(windfile, 'uint16')
        wind.read()
        # convert to Celsius
        wind.data = float32(wind.data)*0.1
    
    sdfilename = "sdfsw_%s.bil" % datetime2BILdate(cdt)
    sdfile = os.path.join(BILout, "sdfsw", str(get_hydroyear(cdt)), sdfilename)
        
    if not os.path.exists(sdfile):
        parser.error("BIL file %s containing snow-depth data does not exist!" %\
                     sdfile)
    else:
        sd = BILdata(sdfile, 'uint16')
        sd.read()
        
    agefilename = "age_%s.bil" % datetime2BILdate(cdt)
    agefile = os.path.join(BILout, "age", str(get_hydroyear(cdt)), agefilename)
        
    if not os.path.exists(agefile):
        parser.error("BIL file %s containing snow-age data does not exist!" %\
                     agefile)
    else:
        age = BILdata(agefile, 'uint8')
        age.read()
    
    lwcfilename = "lwc_%s.bil" % datetime2BILdate(cdt)
    lwcfile = os.path.join(BILout, "lwc", str(get_hydroyear(cdt)), lwcfilename)
        
    if not os.path.exists(lwcfile):
        parser.error("BIL file %s containing snow-LWC data does not exist!" %\
                     lwcfile)
    else:
        lwc = BILdata(lwcfile, 'uint8')
        lwc.read()
#    from pysenorge.tools.show_histogram import Histogram
#    Histogram(sd.data, R=(0, 2000))
    
    # Setup outputs
    outfile = themedir+'_'+datetime2BILdate(cdt)
    outdir = os.path.join(options.outdir, str(get_hydroyear(cdt)))
    if not os.path.exists(outdir):
        if not os.path.exists(options.outdir):
            os.chdir(BILout)
            os.system('mkdir %s' % themedir)
        os.chdir(options.outdir)
        os.system('mkdir %s' % str(get_hydroyear(cdt)))
        
    
    # Calculate additional snow depth due to wind
    #Hwind = __model(wind.data, sd.data)
    Hwind = model(wind.data, sd.data, lwc.data, age.data)
    # Set no-data values to UintFillValue
    mask = senorge_mask()
    Hwind[mask] = UintFillValue
    
    
    if options.bil:
        # Write to BIL file
        bilfile = BILdata(os.path.join(outdir, outfile+'.bil'),
                          datatype='uint16')
        Hwind = uint16(Hwind*1000)
        Hwind[mask] = UintFillValue
        
#        import pylab
#        pylab.imshow(Hwind, vmin=0, vmax=300, cmap=pylab.cm.gist_stern)
#        pylab.colorbar()
#        pylab.show()
        
#        from pysenorge.tools.show_histogram import Histogram
#        Histogram(Hwind, R=(0, 500))
        
        biltext = bilfile.write(Hwind)
        print biltext
    
    if options.nc:
        from pysenorge.io.nc import NCdata
        # Prepare data
        # Change array order 
        ncHwind = flipud(Hwind)
        # Write to NC file
        ncfile = NCdata(os.path.join(outdir, outfile+'.nc'))
        ncfile.zip = True
#        secs = date2num(cdt, timeunit) # used in NCdata.new()
#        ncfile.new(secs)
        ncfile.add_variable(themedir, ncHwind.dtype.str, "m",
                            themename, ncHwind)
        ncfile.close()
    
    if options.png:
        from pysenorge.io.png import writePNG
        # Write to PNG file
        writePNG(flipud(Hwind), os.path.join(outdir, outfile),
                 cltfile=os.path.join(BILout, themedir, "Hwind.clt")
                 )
        
    # At last - cross fingers it all worked out!
    print "\n*** Finished successfully ***\n"
    

if __name__ == '__main__':
    main()
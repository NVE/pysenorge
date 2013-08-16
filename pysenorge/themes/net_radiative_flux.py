'''
Calculation of the net radiative flux:
    Rn = Sn + Ln = Sin (1-alpha) + (Lin + Lout)
    
    where
    Rn: net radiative flux
    Sin: incoming shortwave radiation
    alpha: snow albedo
    Lin, incoming longwave radiation
    Lout: outgoing longwave radiation

@author: kmu
@since: 19. jan. 2011
'''
# Built-in
import os, time
from optparse import OptionParser
# Additional
from netCDF4 import Dataset
from numpy import flipud, add
# Own
from pysenorge.functions.energy_flux import EnergyNetFluxBalance
from pysenorge.set_environment import netCDFin, BILout, FloatFillValue, \
                                      UintFillValue
from pysenorge.io.bil import BILdata
from pysenorge.io.nc import NCdata
from pysenorge.io.png import writePNG
from pysenorge.tools.date_converters import iso2datetime, datetime2BILdate
from pysenorge.converters import nan2fill
from pysenorge.grid import interpolate


def model(SWnet, LWnet, Hs, Hl):
    N = SWnet.shape[0]
    Rnet_array = EnergyNetFluxBalance(SWnet, LWnet, Hs, Hl)
    Rnet = add.reduce(Rnet_array, axis=0) / N
    return Rnet


def main():
    
    # Theme variables
    themedir = 'net_radiative_flux'
    themename = 'Daily avg. net radiation flux'
    
    # Setup input parser
    usage = "usage: python //~HOME/pysenorge/theme_layers/net_radiative_flux.py YYYY-MM-DD [options]"
    
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--timerange", 
                      action="store", dest="timerange", type="string",
                      default="[7,31]",
                      help='''Time-range as "[7,31]"''')
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
    
    # Verify input parameters
    if len(args) != 1:
        parser.error("Please provide the date in ISO format YYYY-MM-DD!")
        parser.print_help() 
    
    # get current datetime
    cdt = iso2datetime(args[0]+" 06:00:00")
    ncfilename = "UM4_sf00_%s.nc" % datetime2BILdate(cdt)
    if len(args) != 1:
        parser.error("Please provide an input file!")
    else:
        # Add full path to the filename
        ncfile = os.path.join(netCDFin, str(cdt.year), ncfilename)
    
    timerange = eval(options.timerange)
    
    if not os.path.exists(ncfile):
        parser.error("%s does not exist!" % ncfile)
    else:
        if timerange == None:
            # Load wind data from prognosis (netCDF file) for entire time-range
            ds = Dataset(ncfile, 'r')
            _time = ds.variables['time'][:]
            SWnet = ds.variables['net_sw_surface'][:,:,:]
            LWnet = ds.variables['net_lw_surface'][:,:,:]
            Hs = ds.variables['sensible_heat_surface'][:,:,:]
            Hl = ds.variables['latent_heat_surface'][:,:,:]
            rlon = ds.variables['rlon'][:]
            rlat = ds.variables['rlat'][:]
            ds.close()
        else:
            # Load wind data from prognosis (netCDF file) for selected time-range
            ds = Dataset(ncfile, 'r')
            _time = ds.variables['time'][timerange[0]:timerange[1]]
            SWnet = ds.variables['net_sw_surface'][timerange[0]:timerange[1],:,:]
            LWnet = ds.variables['net_lw_surface'][timerange[0]:timerange[1],:,:]
            Hs = ds.variables['sensible_heat_surface'][timerange[0]:timerange[1],:,:]
            Hl = ds.variables['latent_heat_surface'][timerange[0]:timerange[1],:,:]
            rlon = ds.variables['rlon'][:]
            rlat = ds.variables['rlat'][:]
            ds.close()
    
    from netCDF4 import num2date
    for t in _time:
        print num2date(t, "seconds since 1970-01-01 00:00:00 +00:00")
            
    # Setup outputs
    tstruct = time.gmtime(_time[-1]) # or -1 if it should be the average until that date
    outfile = '%s_%s_%s_%s' % (themedir, str(tstruct.tm_year).zfill(4),
                               str(tstruct.tm_mon).zfill(2),
                               str(tstruct.tm_mday).zfill(2))
    
    print outfile
    outdir = os.path.join(BILout, themedir, str(cdt.year))
    if not os.path.exists(outdir):
        if not os.path.exists(os.path.join(BILout, themedir)):
            os.chdir(BILout)
            os.system('mkdir %s' % themedir)
        os.chdir(os.path.join(BILout, themedir))
        os.system('mkdir %s' % str(cdt.year))

    # Calculate the wind speed vector - using model()
    Rnet = model(SWnet, LWnet, Hs, Hl)
    
    # interpolate total average wind speed to seNorge grid
    Rnet_intp = interpolate(rlon, rlat, Rnet)
    
    # Replace NaN values with the appropriate FillValue
    Rnet_intp = nan2fill(Rnet_intp)
    
#    # Set no-data values to IntFillValue
#    mask = senorge_mask()
#    tgss[mask] = IntFillValue
#    
#    if options.bil:
#        # Write to BIL file
#        bilfile = BILdata(os.path.join(outdir, outfile+'.bil'),
#                          datatype='int16')
#        biltext = bilfile.write(tgss)
#        print biltext
    
    if options.nc:
        # Prepare data
        # Change array order 
        ncRnet = (Rnet_intp)
        # Write to NC file
        ncfile = NCdata(os.path.join(outdir, outfile+'.nc'))
        ncfile.new(_time[-1])
        ncfile.add_variable(themedir, ncRnet.dtype.str, "W m-2",
                            themename, ncRnet)
        ncfile.close()
    
#    if options.png:
#        from pysenorge.io.png import writePNG
#        # Write to PNG file
#        writePNG(flipud(Rnet_intp), os.path.join(outdir, outfile),
#                 cltfile=os.path.join(BILout, themedir, "tgss.clt")
#                 )
        
    # At last - cross fingers it all worked out!
    print "\n*** Finished successfully ***\n"
    

if __name__ == '__main__':
    main()
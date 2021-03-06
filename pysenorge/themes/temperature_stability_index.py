# -*- coding:UTF-8 -*-
'''

Shows potential changes in snow stability based on temperature and temperature gradient history.

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
execfile("set_pysenorge_path.py") # Adds folder containing the "pysenorge" package to the PYTHONPATH @UnusedImport
from pysenorge.set_environment import METdir, BILout, netCDFout, IntFillValue, UintFillValue
from pysenorge.io.bil import BILdata
from pysenorge.grid import senorge_mask

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
    '''
    ssttm = zeros(tmgr.shape, dtype=uint16)
    dims = tmgr.shape
    print tmgr.shape
    for i in xrange(dims[0]):
        for j in xrange(dims[1]):
            if nodata_mask[i][j]==False: # only consider values that contain data
                if tm[i][j] < -5.0 and tmgr[i][j] > -2.0 and tmgr[i][j] < 2.0:
                    ssttm[i][j] = 1 # unchanged stability
                elif tm[i][j] > -2.0 and tmgr[i][j] < -5.0:
                    ssttm[i][j] = 2 # increased stability
                elif tm[i][j] < -2.0 and tmgr[i][j] > 5.0:
                    ssttm[i][j] = 3 # decreased stability
                    print tmgr[i][j]
                elif tm[i][j] < -2.0 and tmgr[i][j] > 10.0:
                    ssttm[i][j] = 4 # drastically decreased stability
                else:
                    ssttm[i][j] = 0 
    return ssttm
            
def main():
    '''
    Loads and verifies input data, calls the model, and controls the output stream. 
    '''
    # Theme variables
    themedir  = 'ssttm'
    themename = 'Snow stability index (temperature)'
    
    # Setup input parser
    usage = "usage: python //~HOME/pysenorge/themes/temperature_stability_index.py tm_DATE.bil tmgr_DATE.bil [options]"
    
    #Add options
    parser = OptionParser(usage=usage)
    parser.add_option("-o", "--outdir", 
                      action="store", dest="outdir", type="string",
                      metavar="DIR", default=os.path.join(netCDFout, themedir),
                      help="Output directory - default: $netCDFout/%s/$YEAR" % themedir)
    parser.add_option("--no-bil",
                  action="store_false", dest="bil", default=True,
                  help="Set to suppress output in BIL format")
    
    # Comment to suppress help
    #    parser.print_help()
    (options, args) = parser.parse_args()
#         
#     # Verify input parameters
#     if len(args) != 2:
#         parser.print_help()
#         parser.error("Please provide two input files!")
#     else:
#         yy, mm, dd = get_date_filename(args[0])
#         yy_range = arange(1950, 2050)
#         if int(yy) not in yy_range:
#             parser.error("Could not determine year from file name.")
#         # Add full path to the filename
    tmfile = os.path.join(BILout,"temperatur_stability_index", "tm_2012_09_03.bil")
    tmgrfile = os.path.join(BILout,"temperatur_stability_index", "tmgr_2012_09_03.bil")
    yy, mm, dd =  "12","09","03"  
    if not os.path.exists(tmfile):
        parser.print_help()
        parser.error("BIL file containing temperatures does not exist!")
    elif not os.path.exists(tmgrfile):
        parser.print_help()
        parser.error("BIL file containing temperature gradients does not exist!")
    else:
        # Load tm data
        tm = BILdata(tmfile, datatype='uint16')
        tm.read()
        # Load tmgr data 
        tmgr = BILdata(tmgrfile, datatype='int16')
        tmgr.read()
    
    #-----------------------------------------------------------------
    # Setup outputs
    #-----------------------------------------------------------------
    outfile = themedir+'_'+yy+'_'+mm+'_'+dd
    tstring = yy+'-'+mm+'-'+dd+' 06:00:00'
    outdir = os.path.join(options.outdir, yy)
    if not os.path.exists(outdir):
        if not os.path.exists(options.outdir):
            os.chdir(netCDFout)
            os.system('mkdir %s' % themedir)
        os.chdir(options.outdir)
        os.system('mkdir %s' % yy)
    
    #-----------------------------------------------------------------
    # Convert tm to Celsius
    ftm = ((float32(tm.data)-2731) * 0.1)
    mask = senorge_mask()
    
    # Convert tmgr to Celsius
    ftmgr = float32(tmgr.data) * 0.1
    
    # Apply model
    ssttm = model(ftm, ftmgr, mask)
    ssttm[mask] = UintFillValue
    
    if options.bil:
        # Write to BIL file
        bilfile = BILdata(os.path.join(outdir, outfile+'.bil'), datatype="uint16")
        biltext = bilfile.write(ssttm)
        print biltext
       
    # At last - cross fingers it all worked out!
    print "\n*** Finished successfully ***\n"
    
def _view(filename):
    """
    Plot the data contained in the BIL file.
    @requires: I{Matplotlib} module
    """
    try:
        import matplotlib.pyplot as plt
        from pysenorge.grid import senorge_mask
        
        mask = senorge_mask()
        mask = mask==False

        bd = BILdata(filename, datatype='uint16')
        bd.read()
        data = float32(bd.data)*0.1
        
        # Set class values and colors
        colors = ("lightgrey", "g", "b", "m", "r") # class colors
        convalues = [-1,0,1,2,3,4] # contour values
        labvalues = [-0.5, 0.5, 1.5, 2.5, 3.5] # label values
        labels = ["not classified", "unchanged", "increase", "decrease", "drastic decrease"]
        
        plt.figure(facecolor='lightgrey')
        plt.contourf(data, convalues, colors=colors)
        cb = plt.colorbar()
        cb.set_ticks(labvalues)
        cb.set_ticklabels(labels)
        plt.show()
        
    except ImportError:
        print '''Required plotting module "matplotlib" not found!\nVisit www.matplotlib.sf.net'''

def __clt_tsi():
    '''
    Creates CLT file for temperature-stability index bil file.
    '''
    
    from pysenorge.io.png import CLT, HDR, CLTitem
    hdr = HDR(255, 8,
              'Temperatur-stability index',
              '',
              'Stability')
    cltlist = [CLTitem(-0.5, 0.5, (211,211,211), 'not classified'),
               CLTitem(0.5, 1.5, (64, 224, 208), 'unchanged'),
               CLTitem(1.5,2.5, (255,99,71), 'increase'),
               CLTitem(2.5,3.5, (50,205,50), 'decrease'),
               CLTitem(3.5, 4.5, (255,0,0), 'drastic decrease')]
    cltfile = CLT()
    cltfile.new(hdr, cltlist)
    cltfile.write("/home/ralf/Dokumente/summerjob/data/test.clt")
    print 'Created CLT file for temperature-stability index'

if __name__ == "__main__":
    #main()
    __clt_tsi()
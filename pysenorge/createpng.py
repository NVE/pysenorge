import os
from numpy import flipud, float32

#own
from pysenorge.io.bil import BILdata
from pysenorge.io.png import writePNG

def BIL2PNG(BILfile, BILdtype='uint16', CLTfile=None, outdir=os.getcwd()):
    '''
    Convenience function converting the given BIL file to PNG.
    
    @param BILfile: Input BIl file.
    @param outdir: Output directory.
    @param theme_name: Short name for the theme.   
    @param theme_unit: Metric unit of the theme data.
    @param long_name: Descriptive name for the theme. 
    
    @return: PNG file in the output directory.
    '''
    bd = BILdata(BILfile, BILdtype)
    bd.read()
 
    wdata = float32(flipud(bd.data))*0.1
    print wdata.shape
    # Write to PNG file
    writePNG(wdata,"/home/ralf/Dokumente/summerjob/data/test", CLTfile)

BIL2PNG("/home/ralf/Dokumente/summerjob/data/additional_snow_depth_2013_08_17.bil",BILdtype='uint16',
        CLTfile="/home/ralf/Dokumente/summerjob/data/wind_direction_10_no.clt",
        outdir="/home/ralf/Dokumente/summerjob/data/test")

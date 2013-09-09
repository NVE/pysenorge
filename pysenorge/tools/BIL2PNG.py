'''
Doc...

@author: kmu
@since: 1. nov. 2010
'''
# Built-in
import os
import glob
import datetime
# Adds folder containing the "pysenorge" package to the PYTHONPATH @UnusedImport
execfile("./themes/set_pysenorge_path.py") 
# Additional
from numpy import flipud, float32
# Own
from pysenorge.io.bil import BILdata
from pysenorge.io.png import writePNG
from pysenorge.tools.date_converters import datetime2BILdate
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
#    bd._view()
#    bd._hist()
    
    outfile = os.path.splitext(BILfile)[0]
    
    wdata = float32(flipud(bd.data))*0.1
    print wdata.shape
    print type(wdata)
    # Write to PNG file
    writePNG(wdata, os.path.join(outdir, outfile), CLTfile)
    

def _makePeriod(themename, startdate, enddate):
    fl = [] # file list
    dt = datetime.timedelta(days=1)
    while startdate <= enddate:
        fl.append("%s_%s.bil" %(themename, datetime2BILdate(startdate)))
        startdate += dt
    
    return fl 
    
def _depth_hoar_1():
    
    os.chdir(r'Z:\snowsim\depth_hoar_index_1\2011')
#    files = glob.glob('*.bil')
    files = _makePeriod("depth_hoar_index_1",
                        datetime.datetime(year=2010, month=11, day=05),
                        datetime.datetime(year=2010, month=12, day=03))
    for f in files:
        try:
            BIL2PNG(f, 'int16',
                    CLTfile=r'Z:\snowsim\depth_hoar_index_1\dhi1_no.clt',
                    outdir=r'Z:\snowsim\depth_hoar_index_1\2011' 
                    )
        except:
            print "Could not convert %s" % f

def _depth_hoar_2():
    os.chdir(r'Z:\snowsim\depth_hoar_index_2\2011')
#    files = glob.glob('*.bil')
    files = _makePeriod("depth_hoar_index_1",
                        datetime.datetime(year=2010, month=12, day=15),
                        datetime.datetime(year=2011, month=02, day=15))
    for f in files:
        try:
            BIL2PNG(f, 'uint16',
                    CLTfile=r'Z:\snowsim\depth_hoar_index_2\dhi2_no.clt',
                    outdir=r'Z:\snowsim\depth_hoar_index_2\2011')
        except:
            print "Could not convert %s" % f
            
def _wind_direction_1500m():
    
    os.chdir(r'Z:\snowsim\wind_direction_1500m\2011')
    files = glob.glob('*.bil')
    for f in files:
        try:
            BIL2PNG(f, 'uint16',
                    CLTfile=r'Z:\snowsim\wind_direction_1500m\wind_direction_1500_no.clt',
                    outdir=r'Z:\snowsim\wind_1500m_daily\2011')
        except:
            print "Could not convert %s" % f
            
def _wind_speed_avg_10m():
    
    bildir = r'Z:\snowsim\wind_speed_avg_10m\2011'
    os.chdir(bildir)
    files = glob.glob('*.bil')
    for f in files:
        try:
            BIL2PNG(f, 'uint16',
                    CLTfile=r'Z:\snowsim\wind_speed_avg_10m\wind_speed_avg_10m_no_bil.clt',
                    outdir=bildir)
        except:
            print "Could not convert %s" % f
            
def _wind_speed_max_10m():
    
    bildir = r'Z:\snowsim\wind_speed_max_10m\2011'
    os.chdir(bildir)  
    files = glob.glob('*.bil')          
    for f in files:
        try:
            BIL2PNG(f, 'uint16',
                    CLTfile=r"Z:\snowsim\wind_speed_max_10m\wind_speed_max_10m_no_bil.clt",
                    outdir=bildir)
        except:
            print "Could not convert %s" % f
    
def _additional_snow_depth():
    bildir = r'Z:\snowsim\additional_snow_depth\2012'
    os.chdir(bildir)  
    files = glob.glob('*.bil')    
#    files = ['additional_snow_depth_2011_12_13.bil',
#             'additional_snow_depth_2011_10_17.bil',
#             'additional_snow_depth_2011_10_18.bil']
#             'additional_snow_depth_2011_01_20.bil',
#             'additional_snow_depth_2011_01_21.bil',
#             'additional_snow_depth_2011_01_22.bil',
#             'additional_snow_depth_2011_01_23.bil',
#             'additional_snow_depth_2011_01_24.bil',
#             'additional_snow_depth_2011_01_25.bil']      
    for f in files:
#        try:
        BIL2PNG(f, 'uint16',
                CLTfile=r"Z:\snowsim\additional_snow_depth\additional_snow_depth_wind_cat_no.clt",
                outdir=bildir)
#        except:
#            print "Could not convert %s" % f
            
if __name__ == '__main__':
#    _test()
#    _depth_hoar_1()
#    _wind_direction_1500m()
#    _wind_speed_max_10m()
#    _wind_speed_avg_10m()
    _additional_snow_depth()
#    _depth_hoar_2()
# -*- coding:iso-8859-10 -*-
__docformat__ = "reStructuredText"
'''
Script for unzipping the met.no UM4 prognosis from 00:00 every day.

If a start and end date in ISO format is given as separate arguments.
All files between those dates are extracted.

*Note:* The name of the .gz files differs from the unzipped file name.\
Use *gdecompress* to extract the zipped files!

:Author: kmu
:Created: 09. feb. 2011
'''
# Built-in
import sys
import os
import datetime
import gzip

# Define the decompression method
def gdecompress(filename, gzremove=False):
    """
    Unzips the file I{filename}.

    Parameters:
    -----------
    - filename: Gzipped file
    - gzremove: Boolean, if I{True} the original zip file will be deleted. 
    """
    fileObj = gzip.GzipFile(filename, 'rb');
    fileContent = fileObj.readlines();
    fileObj.close()
    
    newname = filename.replace('.gz','')
    fileObjOut = file(newname, 'wb');
    fileObjOut.writelines(fileContent)
    fileObjOut.close()
    
    print "Unzipped file: %s" % os.path.abspath(filename)
    
    if gzremove:
        os.system("rm %s" % filename)
        
    return newname


def todays(basedir):
    cdate = datetime.date.today()
    workdir = os.path.join(basedir, str(cdate.year))
    os.chdir(workdir)
    
    # Convert isodate to filename-date
    cdatestr = str(cdate).replace('-','_')
    
    gdecompress("UM4_ml00_%s.nc.gz" % cdatestr)
    gdecompress("UM4_sf00_%s.nc.gz" % cdatestr)
    print "Finished: %s" % datetime.datetime.now().isoformat()
   
    
def trange(period, basedir):
    from date_converters import iso2datetime, datetime2BILdate
    gzremove=False
    startdate = iso2datetime(period[0]+" 06:00:00")
    enddate = iso2datetime(period[1]+" 06:00:00")
    dt = datetime.timedelta(days=1)
    cdate = startdate
    workdir = os.path.join(basedir, str(cdate.year))
    os.chdir(workdir)
    while cdate <= enddate:
        # Convert isodate to filename-date
        cdatestr = datetime2BILdate(cdate)
        gdecompress("UM4_ml00_%s.nc.gz" % cdatestr, gzremove=gzremove)
        gdecompress("UM4_sf00_%s.nc.gz" % cdatestr, gzremove=gzremove)
        cdate = cdate+dt
    print "Finished: %s" % datetime.datetime.now().isoformat()
        

def main():
    # Set working directory
    if sys.platform == 'win32':
        basedir = 'Z:\metdata\prognosis\um4'
    else:
        basedir = r"/hdata/grid/metdata/prognosis/um4"
    if len(sys.argv) == 1:
        todays(basedir)
    elif len(sys.argv) == 3:
        trange([sys.argv[1], sys.argv[2]], basedir)
    else:
        print "Run without arguments to extract today's files."
        print "Provide start and end ISO dates as separated arguments to define a period."
        
        
if __name__ == "__main__":
    main()
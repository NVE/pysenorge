'''
Script for generating netcdf files containing 24 h of met data.

The script scans through the met input folder and gets a list of netcdf files
with data in the valid time frame.
It determines the earliest date and 06:00 UTC timestamp (- spin-up).
If no output netcdf file exist it clones the structure of the input file.
It fills all variables for the given time range and proceeds to the next input
file.
When 24 h are filled the process starts over again.

@note: The name of the .gz files differs from the unzipped file name.\
Use L{gdecompress} to extract the zipped files!

@author: kmu
@since: 28. okt. 2010
'''
# Built-in
import sys
import os
from optparse import OptionParser
from glob import glob
# Adds folder containing the "pysenorge" package to the PYTHONPATH
execfile(os.path.join(os.path.split(os.path.dirname(__file__))[0],
                      "themes\set_pysenorge_path.py"))
# Additional
from netCDF4 import Dataset, date2num, num2date
from numpy import arange, where, asarray
# Own
from pysenorge.set_environment import timeunit, netCDFout
from pysenorge.tools.clone_netCDF import cloneUM4
from pysenorge.tools.gcompression import gdecompress
from pysenorge.tools.date_converters import iso2datetime, datetime2UMdate
from pysenorge.io.nc import UM4Dataset, NCreport
# Setup input parser
usage = "usage: python generate_daily_met.py YYYY-MM-DD [options]"

parser = OptionParser(usage=usage)
parser.add_option("-d", "--dir", 
                  action="store", dest="wdir", type="string",
                  metavar="DIR", default=os.getcwd(),
                  help="Directory containing the met.no NC files\
                   - default: .")

parser.add_option("-i", "--idstr", 
                  action="store", dest="idstr", type="string",
                  default="sf",
                  help="string identifying the dataset\
                   - options: sf (default) or ml")

parser.add_option("-o", "--offset", 
                  action="store", dest="offset", type="int",
                  default=6,
                  help="Offset in h from the start of the input file\
                  (default=6)")

parser.add_option("-r", "--range", 
                  action="store", dest="hourrange", type="int",
                  default=6,
                  help="Hours to be extract starting from offset\
                  (default=6)")

parser.add_option("--clone",
                  action="store_true", dest="clone", default=False,
                  help="Clone the last netCDF file and fill with 24h of data")

(options, args) = parser.parse_args()

#===============================================================================
# CHECK INPUTS...
#===============================================================================
try:
    enddate = iso2datetime(args[0])
    endsec = date2num(enddate, timeunit)
    print "Given end date: %s (%.2f %s)" %\
    (enddate, endsec, timeunit)
except ValueError:
    errmsg =  "Please insert date in ISO format (YYYY-MM-DDThh:mm:ss)"
    raise ValueError(errmsg)
except IndexError:
    errmsg = "Please provide end date in ISO format (YYYY-MM-DDThh:mm:ss) as first argument"
    raise IndexError(errmsg)

if options.idstr in ["sf", "ml"]:
    pass
else:
    options.idstr = "sf"
    print """Unknown ID string - using default "sf" """

if options.wdir != os.getcwd():
    os.chdir(options.wdir)

#===============================================================================
# Start processing...
#===============================================================================
startsec = endsec - (23*3600.0)
startdate = num2date(startsec, timeunit)
print "Searching date range: %s - %s" % (startdate, enddate)

filesecs = [endsec - (30*3600.0),
            endsec - (24*3600.0),
            endsec - (18*3600.0),
            endsec - (12*3600.0),
            endsec - (6*3600.0)]
filedates = num2date(filesecs, timeunit)
print filedates, type(filedates[0])


# Convert start and end date to the format used in the filename convention.
ncdates = []
for fdate in filedates: 
    ncdates.append(datetime2UMdate(fdate))
print ncdates

# Search for filenames within this range and return list with absolute paths. 
um4files = glob("UM4_%s*.nc" % options.idstr)
metfiles = []
# Look for right dates
for file in um4files:
    for ncdate in ncdates:
        if ncdate in file:
            metfiles.append(file) 
print metfiles

# Include gzipped files
gzum4files = glob("UM4_%s*.nc.gz" % options.idstr)   
gzmetfiles = []
for file in gzum4files:
    for ncdate in ncdates:
        if ncdate in file:
            gzmetfiles.append(file)
print metfiles, gzmetfiles
# unzip if necessary
for file in gzmetfiles:
    if os.path.splitext(file)[0] not in metfiles:
        print "Unzipping %s..." % file 
        metfiles.append(gdecompress(file))
        
metfiles.sort(key=lambda file: file[9:19]) # sorts the file by date only
print metfiles[-1][:6]+metfiles[-1][8:]    


if options.clone:
    # Create 24h data file from most up-to-date data in the metfiles.   
    clonefile = metfiles[-1][:6]+metfiles[-1][8:]
    if not os.path.isfile(clonefile):
        if options.idstr == 'ml':
            cloneUM4(metfiles[-1], clonefile, tn=4, dt=21600.0)
        else:
            cloneUM4(metfiles[-1], clonefile)
    ncdata = UM4Dataset(clonefile, 'a')
    newtimes = num2date(ncdata.variables['time'][:], timeunit)#.tolist()
    print newtimes
    
    # Set the master index for the hours to be extracted
    i = options.offset
    j = options.offset + options.hourrange
    mndx = "%i:%i" % (i, j)
    
    print metfiles
    
    for file in metfiles:
        # read the prognosis file
        ds = Dataset(file, 'r')
        # get relevant times
        dst = ds.variables['time'][i:j]
        # convert to datetime for comparison
        isodst = num2date(dst, timeunit)
        # create the indices
        tndx = []
        mndx = []
        for n in range(len(isodst)):
            ndx = where(newtimes == isodst[n])[0]
            if len(ndx)==1:
                print "Inserting data for date: %s" % isodst[n].isoformat()
                tndx.append(ndx[0])
                mndx.append(i+n)
        tndx = asarray(tndx, int)
        mndx = asarray(mndx, int)
        print mndx, tndx
        # requires index for target file and index for master files
        ncdata.insert(ds, mndx, tndx)
    
    ncdata.close()
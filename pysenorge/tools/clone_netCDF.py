'''
Doc...

@author: kmu
@since: 16. nov. 2010
'''
# Built-in
import time
import datetime
# Additional
from numpy import arange
from netCDF4 import Dataset, num2date, date2num
# Own
from pysenorge.tools.date_converters import iso2datetime
from pysenorge.set_environment import timeunit, default_UM4_width,\
                    default_UM4_height

def cloneUM4(masterfile, newfile, startdate='copy', tn=24, dt=3600.0):
    """
    Creates a new UM4 netCDF file based on a master file.
    
    Convention: Climate and Forecast (CF) version 1.4
    
    @param secs: in seconds since 1970-01-01 00:00:00
    """
    print "Started cloning %s as %s" % (masterfile, newfile)
    
    # open master file
    master = Dataset(masterfile, 'r')
    Mdimensions = master.dimensions.keys()         
        
    # create new file
    rootgrp = Dataset(newfile, 'w', format='NETCDF3_CLASSIC')
    
    # add root dimensions
    rootgrp.createDimension('time', size=tn)
    rootgrp.createDimension('rlon', size=default_UM4_width)
    rootgrp.createDimension('rlat', size=default_UM4_height)
    rootgrp.createDimension('sigma', size=1)
    
    # add root attributes
    rootgrp.Conventions = "CF-1.4"
    rootgrp.institution = "Norwegian Water Resources and Energy Directorate (NVE)"
    rootgrp.source = "Compiled from several +66 hour prognoses by the Norwegian Meteorological Institute (met.no)"
    rootgrp.history = "%s created" % time.ctime(time.time())
    rootgrp.references = "met.no"
    rootgrp.comment = "Progonosis data for www.senorge.no"
    
    # add time variable
    Mtime = master.variables['time']
    # determine start date
    try:
        _end = date2num(iso2datetime(startdate), timeunit)
        _start = _end - ((tn-1) * dt)
    except ValueError:
        # if the startdate is set to "copy" use the date of the last input file
        Mdate = num2date(Mtime[0], timeunit).date()
        utc6 = datetime.time(06, 00, 00)
        _end = date2num(datetime.datetime.combine(Mdate, utc6), timeunit)
        _start = _end - ((tn-1) * dt)
        print (_end-_start)/dt
    _time = rootgrp.createVariable('time', 'f8', ('time',))
    _time[:] = arange(_start, _end+dt, dt) # ensures that _end is included
    for attr in Mtime.ncattrs():
        _time.setncattr(attr, Mtime.getncattr(attr))
    
    # add rlon variable
    Mrlon = master.variables['rlon']
    _rlon = rootgrp.createVariable('rlon', 'f4', ('rlon',))
    _rlon[:] = Mrlon[:]
    for attr in Mrlon.ncattrs():
        _rlon.setncattr(attr, Mrlon.getncattr(attr))
    
    # add rlat variable
    Mrlat = master.variables['rlat']
    _rlat = rootgrp.createVariable('rlat', 'f4', ('rlat',))
    _rlat[:] = Mrlat[:]
    for attr in Mrlat.ncattrs():
        _rlat.setncattr(attr, Mrlat.getncattr(attr))
        
    # add sigma variable
    try:
        Msigma = master.variables['sigma']
        _sigma = rootgrp.createVariable('sigma', 'i2', ('sigma',))
        _sigma[:] = Msigma[:]
        for attr in Msigma.ncattrs():
            _sigma.setncattr(attr, Msigma.getncattr(attr))
    except KeyError:
        print "No variable called 'sigma'!"
    
    for var in master.variables.keys():
        # exclude the variables referring to dimensions
        if var not in Mdimensions:
            exec("M%s = master.variables['%s']" % (var, var))
            exec("print 'Cloning %s', master.variables['%s'].dimensions" % (var, var))
            exec("_%s = rootgrp.createVariable('%s', M%s.dtype, M%s.dimensions)" % (var, var, var, var))
            exec("""for attr in M%s.ncattrs():\n\t_%s.setncattr(attr, M%s.getncattr(attr))""" % (var, var, var))

    rootgrp.close()
    master.close()
    print "Cloning completed!"



if __name__ == '__main__':
    pass
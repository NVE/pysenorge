'''
I{pysenorge} is a package of Python modules for working with I{seNorge} data.
See U{www.senorge.no}.

Requirements
============
    - Python 2.6 - U{http://www.python.org}
    - numpy module - U{http://numpy.scipy.org/}
    - netCDF4 module - U{http://code.google.com/p/netcdf4-python/}
    - pyproj module - U{http://code.google.com/p/pyproj/}
    
Optional
========
    - matplotlib module - U{http://matplotlib.sourceforge.net}
    

@note: Documentation follows the I{epytext} format.

@note: L{pysenorge} package needs to be in PYTHONPATH.
    This is ensured by importing L{theme_layers.set_pysenorge_path}
    
@todo: Use the HPGL library for interpolation such as kriging.\
(debian packages) available
    
@author: kmu
@since: 15. aug. 2010
@organization: Norwegian Water Resources and Energy Direcorate (NVE) - U{www.nve.no}
@contact: U{Karsten Muller<mailto:kmu@nve.no>} 
'''
__docformat__ = 'epytext'

if __name__ == "__main__":
    import test_installation
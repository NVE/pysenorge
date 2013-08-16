"""
Collection of data and unit converters

Input
=====
    - 'M' refers to a matrix/array.
    - 'S' refers to a scalar.

@author: kmu
@since: 17. aug. 2010
"""
# Built-in
import os
# Additional
from numpy import uint16, int8, int16, float32, float64, isnan, load
#Own
from pysenorge.set_environment import UintFillValue, IntFillValue, FloatFillValue, pysenorgedir #@UnresolvedImport

'''DATATYPE CONVERSIONS'''


def dt_simplify(dt):
    """
    Converts numpy datatype to primitive datatype, e.g. float64 > f8
    
    @deprecated: Use numpy.dtype.str instead!
    """
    import warnings
    warnings.warn("Deprecated: Use numpy.dtype.str instead!", DeprecationWarning)
    dtchar = dt.name[0]
    dtbytes = dt.itemsize
    return dtchar+str(dtbytes)


def int2float(M, nodata=int16(IntFillValue)):
    """
    Converts 2-byte signed integer to 4-byte float.
    """
    nodatandx = (M == nodata)
    fM = float32(M)
    fM[nodatandx] = get_FillValue(float32)
    return fM


def uint2float(M, nodata=uint16(UintFillValue)):
    """
    Converts 2-byte unsigned integer to 4-byte float.
    """
    nodatandx = (M == nodata)
    fM = float32(M)
    fM[nodatandx] = get_FillValue(float32)
    return fM


def get_FillValue(dt):
    """
    Determines the FillValue based on the data-type.
    
    No-data values are internally represented as numpy.nan values. These will be replaced by FillValues before writing to BIL or netCDF files. 
    """
    if dt == uint16:
        FillValue = uint16(UintFillValue)
    elif dt == int8:
        FillValue = int8(IntFillValue)
    elif dt == int16:
        FillValue = int16(IntFillValue)
    elif dt == float32:
        FillValue = float32(FloatFillValue)
    elif dt == float64:
        FillValue = float64(FloatFillValue)
    else:
        FillValue = dt(-9999)
    return FillValue


'''UNIT CONVERSIONS''' 
       
def kelvin2celsius(M):
    """
    Converts Kelvin to Celsius.
    """
    return M - 273.15 # CHECK WHICH VALUE IS USED ELSEWHERE


def perday2persec(rate):
    """
    Converts a day rate to per second
    """
    return rate.dtype(rate / (24.0*60.0*60.0))


'''VALUE CONVERSION'''

def nan2fill(A, FillValue=None):
    """
    Replaces numpy's NaN by the data-type fill value.
    
    For default fill values see L{set_environment}.
    """ 
    if FillValue == None:
        FillValue = get_FillValue(A.dtype)
            
    mask = isnan(A)
    A[mask] = FillValue
    
    return A


def set_mask(A):
    FillValue = get_FillValue(A.dtype)
    mask = load(os.path.join(pysenorgedir,"resources/norway_mask.npy"))
    A[mask] = FillValue
    return A
        
        
'''TIME CONVERSION'''

def epoch2date(secs):
    ''' Converts seconds since 1970-01-01 00:00:00 to a date '''
    from time import gmtime
    tstruct = gmtime(secs)
    tstring = "%i-%i-%i %i:%i:%i" % (tstruct.tm_year, tstruct.mon, tstruct.tm_mday, tstruct.tm_hour, tstruct.tm_min, tstruct.tm_sec)
    return tstring


def date2epoch(tstring):
    ''' Converts date to seconds since epoch 1970-01-01 00:00:00 '''
    from calendar import timegm
    from time import strptime
    tstruct = strptime(tstring, "%Y-%m-%d %H:%M:%S")
    secs = float64(timegm(tstruct))
    return secs
    
    

        
'''
UNDER CONSTRUCTION

@author: kmu
@since: 14. sep. 2010
'''
# Built-in
import os, sys

sys.path.append(os.path.abspath('..'))
# Additional
import numpy as np
import numpy.ma as ma
from numpy import arange, meshgrid, ones, where, load, nan

# Own
from pysenorge.set_environment import pysenorgedir

def senorge_grid(meshed=False):
    from pyproj import Proj
    '''
    Creates the seNorge grid.
    
    @param meshed: Flag
    
    @return: x, y 1-D arrays containing the UTM zone 33 coordinates of the senorge grid.
        If I{meshed=True} a x, y meshgrid is returned.
    '''
    # lower left corner in m
    LowerLeftEast = -75000
    LowerLeftNorth = 6450000
    # upper right corner in m
    UpperRightEast = 1120000
    UpperRightNorth = 8000000
    # interval
    dx = 1000
    dy = 1000
    
    x = arange(LowerLeftEast, UpperRightEast, dx)
    y = arange(LowerLeftNorth, UpperRightNorth, dy)
    
    if meshed:
        #Converts vector into coordinate system
        xgrid, ygrid = meshgrid(x, y)
        p = Proj('+proj=utm +zone=33 +ellps=WGS84 +datum=WGS84 +units=m +no_defs')
        lon, lat = p(xgrid, ygrid, inverse=True)
        
        return xgrid, ygrid, lon, lat
    else:
        return x, y

def senorge_mask(show=False):
    """
    Loads the no-data mask for senorge.
    
    @return: Boolean array
    """
    mask = load(os.path.join(pysenorgedir, 'resources/norway_mask.npy'))
    if show:
        try:
            import matplotlib.pyplot as plt
            from matplotlib.cm import Greys
            data = ones(mask.shape)
            data[mask] = 0
            
            plt.figure(facecolor='lightgrey')
            plt.imshow(data, cmap=Greys, alpha=1.0)
            plt.show()
            
        except ImportError:
            print '''Required plotting module "matplotlib" not found!\nVisit www.matplotlib.sf.net'''
    
    return mask
        
def met_grid(ncfile, meshed=False):
    from netCDF4 import Dataset
    '''
    Extracts the UTM converted grid from a met.no netCDF file.
    
    @param ncfile: The netCDF input file.
    @param meshed: Flag
    
    @return: x, y 1-D arrays containing the UTM zone 33 coordinates of the met.no grid.
        If I{meshed=True} a x, y meshgrid is returned.
    '''
    ds = Dataset(ncfile, 'r')
    x = ds.variables['rlon'][:]
    y = ds.variables['rlat'][:]
    ds.close()    
    
    if meshed:
        xgrid, ygrid = meshgrid(x, y)
        return xgrid, ygrid
    else: 
        return x, y
    
def crop_overlap(xin, yin, zin):
    '''
    Crops the input grid to the seNorge grid.
    
    @todo: Ensure that the input grids outline is >= than the seNorge outline 
    '''    
    # Get x,y of senorge grid
    xnve, ynve = senorge_grid()
    
    xmin_ndx = where(xin<xnve.min())[0][-1]
    xmax_ndx = where(xin>xnve.max())[0][0]
    
    ymin_ndx = where(yin<ynve.min())[0][-1]
    ymax_ndx = where(yin>ynve.max())[0][0]

    xinm = xin[xmin_ndx:xmax_ndx+1] 
    yinm = yin[ymin_ndx:ymax_ndx+1]
    zinm = zin[ymin_ndx:ymax_ndx+1, xmin_ndx:xmax_ndx+1]
    return xinm, yinm, zinm

def _view_grid_overlay():
    """
    Test function: visual check for crop_overlay().
    """
    from matplotlib.patches import Rectangle
    import matplotlib.pyplot as plt
    
    xnve, ynve = senorge_grid()
    xmet, ymet = met_grid(r"Z:\metdata\prognosis\UM4_for_snomodellering\201006\UM4sf_2010063012.nc")
    
    zmet = ones((ymet.size, xmet.size)) + 1.0
    print xmet.shape, ymet.shape, zmet.shape
    xmet, ymet, zmet = crop_overlap(xmet, ymet, zmet)
    print xmet.shape, ymet.shape, zmet.shape
    
    print "NVE"
    print "xy(0-1, 0-1): (%f, %f) (%f, %f)" %\
        (xnve[0], ynve[0], xnve[1], ynve[1])
    print "xy(-2--1, -2--1)", xnve[-2], ynve[-2], xnve[-1], ynve[-1] 
    print "\nMET"
    print "xy(0-1, 0-1)", xmet[0], ymet[0], xmet[1], ymet[1]
    print "xy(-2--1, -2--1)", xmet[-2], ymet[-2], xmet[-1], ymet[-1] 
    
    print "Start plotting..."
     
    plt.figure()
    plt.hold(True)
    
    metgrid = Rectangle((xmet[0], ymet[0]), (xmet[-1] - xmet[0]), (ymet[-1] - ymet[0]),
              fc='r', alpha=0.5)#, fill=True, zorder=1)
    plt.gca().add_patch(metgrid)
    
    metcell = Rectangle((xmet[0], ymet[0]), (xmet[1] - xmet[0]), (ymet[1] - ymet[0]),
              fc='r', alpha=0.7)#, fill=True, zorder=1)
    plt.gca().add_patch(metcell)
    
    nvegrid = Rectangle((xnve[0], ynve[0]), (xnve[-1] - xnve[0]), (ynve[-1] - ynve[0]),
              fc='g', alpha=0.5)#, fill=True, zorder=1)
    plt.gca().add_patch(nvegrid)
    
    nvecell = Rectangle((xnve[0], ynve[0]), (xnve[1] - xnve[0]), (ynve[1] - ynve[0]),
              fc='g', alpha=0.7)#, fill=True, zorder=1)
    plt.gca().add_patch(nvecell)
    
    plt.scatter([xnve[0], xnve[1]], [ynve[0], ynve[1]], marker='+', s=50)
    plt.scatter([xnve[-2], xnve[-1]], [ynve[-2], ynve[-1]], marker='+', s=50)
    plt.scatter([xmet[0], xmet[1]], [ymet[0], ymet[1]], marker='x', s=50)
    plt.scatter([xmet[-2], xmet[-1]], [ymet[-2], ymet[-1]], marker='x', s=50)
    plt.show()

###############################################################################
### These functions are from matplotlib.cbook by Jeffrey Whitaker #############
###############################################################################

def iterable(obj):
    'return true if *obj* is iterable'
    try: len(obj)
    except: return False
    return True

def is_string_like(obj):
    'Return True if *obj* looks like a string'
    if isinstance(obj, (str, unicode)): return True
    # numpy strings are subclass of str, ma strings are not
    if ma.isMaskedArray(obj):
        if obj.ndim == 0 and obj.dtype.kind in 'SU':
            return True
        else:
            return False
    try: obj + ''
    except: return False
    return True

def is_scalar(obj):
    'return true if *obj* is not string like and is not iterable'
    return not is_string_like(obj) and not iterable(obj)

###############################################################################

def interp(datain,xin,yin,xout,yout,checkbounds=False,masked=False,order=1):
    """This function is originally from matplotlib.toolkits.basemap.interp
    
    Copyright 2008, Jeffrey Whitaker
    
    Interpolate data (``datain``) on a rectilinear grid (with x = ``xin``
    y = ``yin``) to a grid with x = ``xout``, y= ``yout``.

    .. tabularcolumns:: |l|L|

    ==============   ====================================================
    Arguments        Description
    ==============   ====================================================
    datain           a rank-2 array with 1st dimension corresponding to
                     y, 2nd dimension x.
    xin, yin         rank-1 arrays containing x and y of
                     datain grid in increasing order.
    xout, yout       rank-2 arrays containing x and y of desired output grid.
    ==============   ====================================================

    .. tabularcolumns:: |l|L|

    ==============   ====================================================
    Keywords         Description
    ==============   ====================================================
    checkbounds      If True, values of xout and yout are checked to see
                     that they lie within the range specified by xin
                     and xin.
                     If False, and xout,yout are outside xin,yin,
                     interpolated values will be clipped to values on
                     boundary of input grid (xin,yin)
                     Default is False.
    masked           If True, points outside the range of xin and yin
                     are masked (in a masked array).
                     If masked is set to a number, then
                     points outside the range of xin and yin will be
                     set to that number. Default False.
    order            0 for nearest-neighbor interpolation, 1 for
                     bilinear interpolation, 3 for cublic spline
                     (default 1). order=3 requires scipy.ndimage.
    ==============   ====================================================

    .. note::
     If datain is a masked array and order=1 (bilinear interpolation) is
     used, elements of dataout will be masked if any of the four surrounding
     points in datain are masked.  To avoid this, do the interpolation in two
     passes, first with order=1 (producing dataout1), then with order=0
     (producing dataout2).  Then replace all the masked values in dataout1
     with the corresponding elements in dataout2 (using numpy.where).
     This effectively uses nearest neighbor interpolation if any of the
     four surrounding points in datain are masked, and bilinear interpolation
     otherwise.

    Returns ``dataout``, the interpolated data on the grid ``xout, yout``.
    """    
    # xin and yin must be monotonically increasing.
    if xin[-1]-xin[0] < 0 or yin[-1]-yin[0] < 0:
        raise ValueError, 'xin and yin must be increasing!'
    if xout.shape != yout.shape:
        raise ValueError, 'xout and yout must have same shape!'
    # check that xout,yout are
    # within region defined by xin,yin.
    if checkbounds:
        if xout.min() < xin.min() or \
           xout.max() > xin.max() or \
           yout.min() < yin.min() or \
           yout.max() > yin.max():
            raise ValueError, 'yout or xout outside range of yin or xin'
    # compute grid coordinates of output grid.
    delx = xin[1:]-xin[0:-1]
    dely = yin[1:]-yin[0:-1]
    if max(delx)-min(delx) < 1.e-4 and max(dely)-min(dely) < 1.e-4:
        # regular input grid.
        xcoords = (len(xin)-1)*(xout-xin[0])/(xin[-1]-xin[0])
        ycoords = (len(yin)-1)*(yout-yin[0])/(yin[-1]-yin[0])
    else:
        # irregular (but still rectilinear) input grid.
        xoutflat = xout.flatten(); youtflat = yout.flatten()
        ix = (np.searchsorted(xin,xoutflat)-1).tolist()
        iy = (np.searchsorted(yin,youtflat)-1).tolist()
        xoutflat = xoutflat.tolist(); xin = xin.tolist()
        youtflat = youtflat.tolist(); yin = yin.tolist()
        xcoords = []; ycoords = []
        for n,i in enumerate(ix):
            if i < 0:
                xcoords.append(-1) # outside of range on xin (lower end)
            elif i >= len(xin)-1:
                xcoords.append(len(xin)) # outside range on upper end.
            else:
                xcoords.append(float(i)+(xoutflat[n]-xin[i])/(xin[i+1]-xin[i]))
        for m,j in enumerate(iy):
            if j < 0:
                ycoords.append(-1) # outside of range of yin (on lower end)
            elif j >= len(yin)-1:
                ycoords.append(len(yin)) # outside range on upper end
            else:
                ycoords.append(float(j)+(youtflat[m]-yin[j])/(yin[j+1]-yin[j]))
        xcoords = np.reshape(xcoords,xout.shape)
        ycoords = np.reshape(ycoords,yout.shape)
    # data outside range xin,yin will be clipped to
    # values on boundary.
    if masked:
        xmask = np.logical_or(np.less(xcoords,0),np.greater(xcoords,len(xin)-1))
        ymask = np.logical_or(np.less(ycoords,0),np.greater(ycoords,len(yin)-1))
        xymask = np.logical_or(xmask,ymask)
    xcoords = np.clip(xcoords,0,len(xin)-1)
    ycoords = np.clip(ycoords,0,len(yin)-1)
    # interpolate to output grid using bilinear interpolation.
    if order == 1:
        xi = xcoords.astype(np.int32)
        yi = ycoords.astype(np.int32)
        xip1 = xi+1
        yip1 = yi+1
        xip1 = np.clip(xip1,0,len(xin)-1)
        yip1 = np.clip(yip1,0,len(yin)-1)
        delx = xcoords-xi.astype(np.float32)
        dely = ycoords-yi.astype(np.float32)
        dataout = (1.-delx)*(1.-dely)*datain[yi,xi] + \
                  delx*dely*datain[yip1,xip1] + \
                  (1.-delx)*dely*datain[yip1,xi] + \
                  delx*(1.-dely)*datain[yi,xip1]
    elif order == 0:
        xcoordsi = np.around(xcoords).astype(np.int32)
        ycoordsi = np.around(ycoords).astype(np.int32)
        dataout = datain[ycoordsi,xcoordsi]
    elif order == 3:
        try:
            from scipy.ndimage import map_coordinates
        except ImportError:
            raise ValueError('scipy.ndimage must be installed if order=3')
        coords = [ycoords,xcoords]
        dataout = map_coordinates(datain,coords,order=3,mode='nearest')
    else:
        raise ValueError,'order keyword must be 0, 1 or 3'
    if masked and isinstance(masked,bool):
        dataout = ma.masked_array(dataout)
        newmask = ma.mask_or(ma.getmask(dataout), xymask)
        dataout = ma.masked_array(dataout,mask=newmask)
    elif masked and is_scalar(masked):
        dataout = np.where(xymask,masked,dataout)
    return dataout


def interpolate(xold, yold, zold):
    """
    Convenience function for interpolating the UM4 grid to the seNorge grid. 
    """
#    print xold.shape, yold.shape, zold.shape

    xcrop, ycrop, zcrop = crop_overlap(xold, yold, zold)
    xcrop, ycrop, zcrop = xold, yold, zold
#    print xcrop.shape, ycrop.shape, zcrop.shape
#    print xcrop[0], xcrop[-1], ycrop[0], ycrop[-1]
    xnew, ynew, lon, lat = senorge_grid(meshed=True) #@UnusedVariable
    
    znew = interp(zcrop, xcrop, ycrop, xnew, ynew, checkbounds=True, masked=False, order=0)
    
#     new_znew=zold
#     
#     print type(new_znew)
#     print type(znew)
#     
#     print new_znew.shape 
#     print znew.shape 
#     
#     print new_znew[100,100]
#     print znew[100,100]

    znew = zold
    
#   print xnew.shape, ynew.shape, znew.shape
    mask = np.flipud(np.load(os.path.join(pysenorgedir, 'resources/norway_mask.npy')))
    znew[mask]  = nan
#   from pylab import figure, imshow, show
#   imshow(znew)
#   figure()
#   imshow(zcrop)
#   figure()
#   imshow(zold)
#   show()
    
    return znew


def interpolate_new(zold):
    """
    Old declaration:Convenience function for interpolating the UM4 grid to the seNorge grid.
    After change to Arome Modell no need to interpolate and breaking down of the inputgrid
    """
    xnew, ynew, lon, lat = senorge_grid(meshed=True) #@UnusedVariable
    
    znew = zold
    
    mask = np.flipud(np.load(os.path.join(pysenorgedir, 'resources/norway_mask.npy')))
    
    znew[mask]  = nan
    
    return znew
    
if __name__ == '__main__':
#    x, y, lon, lat = senorge_grid(True)
#    print lon.shape
#    print lat.shape
    _view_grid_overlay()
#    interpolate()
#    senorge_mask(True)
__docformat__ = "reStructuredText"
'''
Binary (.bil) input/output class.

:Author: kmu
:Created: 14. okt. 2010
'''
# Built-in
import os, sys
sys.path.append(os.path.abspath('../..'))

# Additional
from numpy import zeros, fromfile, int8, int16, uint8, uint16, float32, nan

# Own
from pysenorge.converters import get_FillValue


class BILdata(object):
    '''
    Class for reading, writing and displaying BIL format files for 
    *www.senorge.no*.
    
    The seNorge array has a standard size of height=1550, width=1195.
    The standard data-type is "uint16" with a no-data-value of 65535.
    The standard file name is of type "themename_YYYY_MM_DD.bil"  
    '''

    def __init__(self, filename, datatype):
        '''
        Initializes defaults.
        '''
        self.nrows = 1550
        self.ncols = 1195
        self.datatype = eval(datatype)
        self.nodata = get_FillValue(self.datatype)
        self.data = zeros((self.nrows, self.ncols), self.datatype)
        self.filename = filename
        
        
    def _set_dimension(self, nrows, ncols):
        '''
        Override standard dimensions.
        
        :Parameters:
            - nrows: Number of new rows
            - ncols: Number of new columns  
        '''
        self.nrows = nrows
        self.ncols = ncols
        self.data = zeros((self.nrows, self.ncols), self.datatype)
        
    
    def read(self):
        """
        Reads data from BIL file.
        """
        print "Reading %s" % self.filename
#        self._read_hdr()
        fid = open(self.filename, "rb")
        tmpdata = fromfile(fid, self.datatype)
        fid.close()
        tmpdata.shape = (self.nrows, self.ncols)
        self.data[:] = tmpdata
#        self._get_mask()


    def write(self, data):
        '''
        Writes data to BIL file.
        
        :Parameters:
            - data: *numpy* array to be stored
        '''
        # Make sure data is in appropriate format
        if self.data.dtype == data.dtype:
            # Open and write to file
            fid = open(self.filename, 'wb')
            fid.write(data)
            fid.flush()
            fid.close()
            self.data = data
            return "Data written to %s" % self.filename
        else:
            print "Inconsistent data-type for BIL format."
            
            
    def _read_hdr(self):
        """
        Reads header information from *.hdr* file (if existent).
        """
        hdr = os.path.splitext(self.filename)[0] + '.hdr'
        if os.path.exists(hdr):
            # Verify the information
            fid = open(hdr, 'r')
            lines = fid.readlines()
            byteorder = int(lines[0].split('\t')[1].strip())
            nrows = int(lines[2].split('\t')[1].strip())
            ncols = int(lines[3].split('\t')[1].strip())
            print "BYTEORDER: %i \nNROWS: %i \nNCOLS: %i\n" % (byteorder, nrows, ncols)
            self._set_dimension(nrows, ncols)
        else:
            print "No header data found! Using default..."
              
    
    def _write_hdr(self):
        ''' 
        Creates a I{.hdr} file to the corresponding I{.bil} file.

        Example content of .hdr file
        BYTEORDER      I
        LAYOUT       BIL
        NROWS         1550
        NCOLS         1195
        NBANDS        1
        NBITS         16
        BANDROWBYTES         2390
        TOTALROWBYTES        2390
        BANDGAPBYTES         0
        '''
        hdr = os.path.splitext(self.filename)[0] + '.hdr'
        fid = open(hdr, 'w')
        fid.write('BYTEORDER\t%s\n' % sys.byteorder)
        fid.write('LAYOUT\tBIL\n')
        fid.write('NROWS\t%i\n' % self.nrows)
        fid.write('NCOLS\t%i\n' % self.ncols)
        fid.write('NBANDS\t1\n')
        fid.write('NBITS\t16\n')
        fid.write('BANDROWBYTES\t2390\n')
        fid.write('TOTALROWBYTES\t2390\n')
        fid.write('BANDGAPBYTES\t0\n')
        fid.flush()
        fid.close()   
        
        
    def _view(self):
        """
        Plot the data contained in the BIL file.
        
        :Requires: *Matplotlib* module
        """
        try:
            import matplotlib.pyplot as plt
            from matplotlib.cm import jet
            from pysenorge.grid import senorge_mask
            
            mask = senorge_mask()
            data = float32(self.data)
            data[mask] = nan
            
            plt.figure(facecolor='lightgrey')
            plt.imshow(data, interpolation='nearest', cmap=jet, alpha=1.0,
#                       vmin=-1, vmax=0
                       )

            plt.colorbar()
            plt.show()
            
        except ImportError:
            print '''Required plotting module "matplotlib" not found!\nVisit www.matplotlib.sf.net'''
            
            
    def _hist(self):
        """
        Histogram of the data contained in the BIL file.
        
        :Requires: *Matplotlib* module
        """
        try:
            import matplotlib.pyplot as plt     
            plt.hist(self.data, 30, histtype='barstacked', align='left')
            plt.show()
            
        except ImportError:
            print '''Required plotting module "matplotlib" not found!\nVisit www.matplotlib.sf.net'''
                
        
    
    
if __name__ == "__main__":
    pass
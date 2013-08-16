# -*- coding:iso-8859-10 -*-
__docformat__ = 'restructuredtext'
'''
Output to PNG image files.

:Author: kmu
:Created: 14. okt. 2010
'''
# Built-in
# Additional
# Own

def writePNG(A, outname, cltfile=None, test=False, vmin=0, vmax=100):
    """
    Write PNG image using *Matplotlib*.
    
    :Parameters:
        - A: Input array containing the values to be plotted.
        - outname: Name of the output image file. 
    """
    try:
        import matplotlib
#        matplotlib.rcParams['text.latex.unicode'] = True
#        if sys.platform == 'linux2': 
        matplotlib.rcParams['backend'] = 'TkAgg' # set to common Tk backend to avoid conflicts on linux machine
#        else:
#            matplotlib.rcParams['backend'] = 'WxAgg'

        import matplotlib.pyplot as plt
        
        # Plot resulting layer
        fig = plt.figure(figsize=(11.95, 15.50), facecolor='lightgrey')
        ax = fig.add_subplot(111)
#        fig.subplots_adjust(left=0.0, bottom=0.0, right=1.0, top=1.0) 
        
        if cltfile == None:
            plt.imshow(A, vmin=vmin, vmax=vmax)
            plt.colorbar()
            plt.show()
        else:
            clt = CLT()
            clt.read(cltfile)
            colors, contours, ticks, labels = clt.forMPL()

            ax.contourf(A, contours, colors=colors, aspect='equal',
                               label=clt.hdr.header1)

            _pngColorbar(fig, colors, contours, ticks, labels, clt.hdr.legend)
            plt.figtext(0.16, 0.84, clt.hdr.header2.replace(' - ', '\n'))
        
            if test:
                plt.title = clt.hdr.header1
                plt.show()
            else:
                ax.axis('off')
                # dpi x figsize = 1550x1195 pixel
                plt.savefig(outname+".png", dpi=100)
                print "%s written!" % (outname+".png")
            
    except ImportError:
        print '''Required plotting module "matplotlib" not found!\nVisit www.matplotlib.sf.net''' 

    
def _pngColorbar(fig, colors, contours, ticks, labels, title):
    from matplotlib import mpl
    # ColorbarBase derives from ScalarMappable and puts a colorbar
    # in a specified axes, so it has everything needed for a
    # standalone colorbar.  There are many more kwargs, but the
    # following gives a basic continuous colorbar with ticks
    # and labels.    
    cbax = fig.add_axes([0.6, 0.15, 0.1, 0.17])
    # The second example illustrates the use of a ListedColormap, a
    # BoundaryNorm, and extended ends to show the "over" and "under"
    # value colors.
    cmap = mpl.colors.ListedColormap(colors)
    
    # If a ListedColormap is used, the length of the bounds array must be
    # one greater than the length of the color list.  The bounds must be
    # monotonically increasing.
    norm = mpl.colors.BoundaryNorm(contours, cmap.N)
    cb = mpl.colorbar.ColorbarBase(cbax, cmap=cmap,
                                         norm=norm,
                                         spacing='uniform',
                                         orientation='vertical')
    cb.ax.set_xlabel(title)
    cb.ax.xaxis.set_label_position('top')
    
    cb.set_ticks(contours)    
    cb.ax.set_yticklabels(labels, fontsize=11, va='baseline')
    

class HDR():
    """
    The color look-up table header class.
    """
    def __init__(self, nodata, nobits, header1, header2, legend):
        self.nodata = nodata
        self.nobits = nobits
        self.header1 = header1
        self.header2 = header2
        self.legend = legend
        
    def __str__(self):
        return "nodata\t%s\nnobits\t%s\nheader1\t*%s\nheader2\t*%s\nlegend\t*%s"%\
                (str(self.nodata),
                 str(self.nobits),
                 self.header1,
                 self.header2,
                 self.legend)
        
        
class CLTitem():
    """
    The color look-up table item class.
    """
    def __init__(self, FROM, TO, RGB, TXT):
        self.FROM = FROM
        self.TO = TO
        self.RGB = RGB
        self.TXT = TXT
        
    def __str__(self):
        return "%s\t%s\t%i\t%i\t%i\t*%s" % (str(self.FROM), str(self.TO),
                                           self.RGB[0],self.RGB[1], self.RGB[2],
                                           self.TXT)
        
class CLT():
    """
    The color look-up table class.
    """
    
    def __init__(self):
        self.explanation = "From\tTo\tR\tG\tB\tExplanation"
        self.cltlist = []
    
    def new(self, HDR, CLTlist):
        """
        Init a new instance.
        """
        self.hdr = HDR
        self.cltlist = CLTlist
        
        
    def str2num(self, s):
        """
        Convert string to either integer or float.
        
        :Parameters:
            - s: String
        
        :Returns:
            - num: Integer or float
        """
        try:
            num = int(s)
        except ValueError:
            num = float(s)
        return num
    
    
    def write(self, cltfile):
        import codecs
        
        fid = codecs.open(cltfile, 'w', encoding='iso-8859-10')
        fid.write(self.hdr.__str__())
        fid.write('\n')
        fid.write(self.explanation)
        for cltitem in self.cltlist:
            fid.write('\n')
            fid.write(cltitem.__str__())
        fid.close()
        
        
    def read(self, cltfile):
        import codecs
        """
        Read header and color data from a .clt file.
        
        .. warning:: Currently the code will not work if there are additional empty lines at the EOF.
        
        :Parameters:
            - cltfile: Text file containing the header and color data.    
        """
        fid = codecs.open(cltfile, 'r', encoding='iso-8859-10')
        lines = fid.readlines()
        fid.close()
        
        N = len(lines)
        
        # Read out header info
        self.hdr = HDR(self.str2num(lines[0].split('\t')[1]),
                       self.str2num(lines[1].split('\t')[1]),
                       lines[2].split('*')[1].strip(),
                       lines[3].split('*')[1].strip(),
                       lines[4].split('*')[1].strip())
        
        # Read out colors
        for n in xrange(6, N):
            cont = lines[n].split('\t')
            if len(cont) < 6:
                break # exit loop when reaching end of file or empty line
            clti = CLTitem(self.str2num(cont[0]),
                           self.str2num(cont[1]),
                           (int(cont[2]), int(cont[3]), int(cont[4])),
                           lines[n].split('*')[1].strip())
  
            self.cltlist.append(clti)
    
    
    def _FROM_cmp(self, clt1, clt2):
        """
        Helper function to sort cltlist by the clt.FROM object.
        Required in "forMPL()".
        """
        return cmp(clt1.FROM, clt2.FROM)


    def forMPL(self):
        """
        Returns header and color data for use in a *Matplotlib* contour plot.
        
        :Parameters:
            - hdr: Header from readCLT
            - clt_list: CLT list from readCLT
            
        :Returns:
            - Colors, contours, ticks, and labels for a I{Matplotlib} contour plot
        """
        self.cltlist.sort(self._FROM_cmp)
        rgbmax = 255.0
        colors = []
        contours = []
        ticks = []
        labels = []
        for clt in self.cltlist:
            colors.append((clt.RGB[0]/rgbmax, clt.RGB[1]/rgbmax, clt.RGB[2]/rgbmax))
            contours.append(clt.FROM)
            ticks.append(clt.FROM+(clt.TO-clt.FROM)/2)
            labels.append(clt.TXT)
        contours.append(self.cltlist[-1].TO)

        return colors, contours, ticks, labels


def _test():
    cltfile = CLT()
    cltfile.read(r"Z:\tmp\average_wind_speed\awsd.clt")
    print cltfile.hdr
    for clt in cltfile.cltlist:
        print clt
    cltfile.write(r"Z:\tmp\average_wind_speed\awsd600.clt")
        
        
if __name__ == "__main__":
    _test()
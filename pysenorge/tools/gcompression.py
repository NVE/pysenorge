'''
De/Compress files using the gzip library.

@author: kmu
@since: 9. nov. 2010
'''
# Built-in
import os
import gzip
import time


def gdecompress(filename, gzremove=False):
    """
    Unzips the file I{filename}.
    
    @param filename: Gzipped file
    @param gzremove: Boolean, if I{True} the original zip file will be deleted. 
    """
    fileObj = gzip.GzipFile(filename, 'rb');
    fileContent = fileObj.readlines();
    fileObj.close()
    
    newname = filename.replace('.gz','')
    fileObjOut = file(newname, 'wb');
    fileObjOut.writelines(fileContent)
    fileObjOut.close()
    
    statinfo = os.stat(newname)
    print "Unzipped file: %s" % os.path.abspath(filename)
    print "Time of creation:", time.ctime(statinfo.st_ctime)
    print "Time of last access:", time.ctime(statinfo.st_atime)
    
    if gzremove:
        os.system("rm %s" % filename)
        
    return newname
    
    
def gcompress(filename, outdir=os.getcwd()):
    """
    Gzips the file I{filename}.
    
    @param filename: The file(path) to be gzipped.
    @param outdir: Folder where the zipped file is stored - default=current.
    """
    fileObj = open(filename, 'rb')
    fileObjOut = gzip.open(os.path.join(outdir,
                                        os.path.basename(filename)+'.gz'),
                                        'wb')
    fileObjOut.writelines(fileObj)
    fileObjOut.close()
    fileObj.close()
    
    
if __name__ == "__main__":
    wdir = (r"Z:\metdata\prognosis\um4\2010")
    filename = "UM4_sf00_2010_11_09.nc.gz"
    os.chdir(wdir)    
    
    gdecompress(filename)
#    gcompress(filename.replace('.gz',''), outdir=r"Z:\tmp")
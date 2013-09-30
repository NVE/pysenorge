'''
Created on 12.09.2013

@author: Ralf Loritz
'''

# Built-in

# Additional
import numpy as np

#Own
from pysenorge.io.bil import BILdata


class frozen:
    def load_data(self, ssttm): 
        tsi = BILdata(ssttm, datatype='uint16')
        tsi.read()
        self.tsi = tsi.data

    def check_value(self, tsi):
        self.idex = np.where(tsi==2)

if __name__ == "__main__":
    tst = frozen()
    tst.load_data('/home/ralf/Dokumente/summerjob/data/netCDF/ssttm/12/ssttm_12_09_03.bil')
    tst.check_value(tst.tsi)

    print tst.idex    
'''
Tests the BILdata class.

@author: kmu
@since: 12. okt. 2010
'''
import unittest, sys, os
sys.path.insert(0,os.path.abspath('../..'))

from numpy import uint16, ones
from pysenorge.io.bil import BILdata

class Test(unittest.TestCase):


    def testName(self):
        # Create an array
#        A = arange(1852250, dtype=uint16)
        A = ones((1550,1195), dtype=uint16)
        print A
        
        # Store it in .bil format
        bd = BILdata("tmp_test.bil")
#        bd.set_dimension(4,3)
        bd.write(A)
        print bd.datatype
        
        # Open .bil file
        bdo = BILdata("tmp_test.bil")
#        bdo.set_dimension(4,3)
        bdo.read()
        print bdo.data
        # Assert if data from bil file is equal to the inital array
        self.assertEqual(A.all, bdo.data.all, "Not equal")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
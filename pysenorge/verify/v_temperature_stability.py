# -*- coding:UTF-8 -*-
'''
Unittest for the L{themes.temperature_stability} theme.

@author: kmu
@since: 6. okt. 2010
'''

import unittest, sys, os
sys.path.insert(0, os.path.abspath('../..'))

from numpy import asarray
from pysenorge.themes.temperature_stability import model

class Test(unittest.TestCase):

    def test_cat0(self):
        tm = asarray(
                     [[-15]]
                     )
        
        tmgr = asarray(
                       [[5]]
                       )
        
        tmcat = model(tm, tmgr)
        self.assertEqual(tmcat[0][0], 0, 'Category should be 0. Got %f instead' % (tmcat[0][0]))
     
        
    def test_cat3(self):
        tm = asarray(
                     [[-8]]
                     )
        
        tmgr = asarray(
                       [[6]]
                       )
        
        tmcat = model(tm, tmgr)
        self.assertEqual(tmcat[0][0], 3, 'Category should be 3. Got %f instead' % (tmcat[0][0]))
        
    
    def test_cat4(self):
        tm = asarray(
                     [[-1]]
                     )
        
        tmgr = asarray(
                       [[-8]]
                       )
        
        tmcat = model(tm, tmgr)
        self.assertEqual(tmcat[0][0], 4, 'Category should be 4. Got %f instead' % (tmcat[0][0]))
    
        
    def test_cat5(self):
        tm = asarray(
                     [[-15]]
                     )
        
        tmgr = asarray(
                       [[-1]]
                       )
        
        tmcat = model(tm, tmgr)
        self.assertEqual(tmcat[0][0], 5, 'Category should be 5. Got %f instead' % (tmcat[0][0]))
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_on_random_array']
    unittest.main()
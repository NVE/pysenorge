'''
Unittest for the L{themes.temperature_gradient_daily} theme.

@author: kmu
@since: 10. aug. 2010
'''

import unittest, sys, os
sys.path.insert(0,os.path.abspath('../..'))
print sys.path 
from pysenorge.themes.temperature_gradient_daily import model #@UnresolvedImport

class Test(unittest.TestCase):

    def test_neg2neg_down(self):
        T0 = -10.0
        T1 = -5.0
        dT = -5.0
        grad = model(T0, T1)
        self.assertEqual(grad, dT, 'Gradient should be equal to %f. Got %f instead' % (dT, grad))
        
    def test_neg2neg_up(self):
        T0 = -2.0
        T1 = -6.0
        dT = +4.0
        grad = model(T0, T1)
        self.assertEqual(grad, dT, 'Gradient should be equal to %f. Got %f instead' % (dT, grad))
    
    def test_pos2pos_up(self):
        T0 = +7.0
        T1 = +1.0
        dT = +6.0
        grad = model(T0, T1)
        self.assertEqual(grad, dT, 'Gradient should be equal to %f. Got %f instead' % (dT, grad))
        
    def test_pos2pos_down(self):
        T0 = +3.0
        T1 = +6.0
        dT = -3.0
        grad = model(T0, T1)
        self.assertEqual(grad, dT, 'Gradient should be equal to %f. Got %f instead' % (dT, grad))
            
    def test_neg2pos(self):
        T0 = +2.0
        T1 = -5.0
        dT = +7.0
        grad = model(T0, T1)
        self.assertEqual(grad, dT, 'Gradient should be equal to %f. Got %f instead' % (dT, grad))
        
    def test_pos2neg(self):
        T0 = -12.0
        T1 = +5.0
        dT = -17.0
        grad = model(T0, T1)
        self.assertEqual(grad, dT, 'Gradient should be equal to %f. Got %f instead' % (dT, grad))
        
        
if __name__ == "__main__":
    unittest.main()
__doc_format__ = "reStructuredText"
'''
Doc...

:Author: kmu
:Created: 3. may 2011
:Changed: 6. may 2011 - added WindThresholdLi()
'''

''' Imports '''
# Built-in
import math
# Additional

# Own
from pysenorge.constants import rho_air

def WindPointsNorem():
    pass


def AdditionalSnowDepth(u, Umax=20.0):
    '''
    Additional snow depth over 24 h derived for the average 10 m wind speed over
    a mountain crest. No threshold wind speed is used since the model was only
    evaluated under snow-storm conditions, where even very low wind speeds are
    sufficient to transport snow.
    
    **References:** Foehn (1980)
    
    :Parameters:
        * u: average daily wind speed [m/s]
        * Umax: wind transport normally becomes ineffective above this value [m/s]
    
    :Returns:
        * Hwind: additional snow height due to wind transport 
    '''

    if u>Umax:
        u = Umax
    k = 8e-5 # [s3 d-1 m-2]
    Hwind = k * u**3
    
    return Hwind


def WindThresholdLi(T):
    '''
    **Reference:**
        Li, L., & Pomeroy, J. W. (1997). Estimates of Threshold Wind Speeds for Snow Transport Using Meteorological Data. Journal of Applied Meteorology, 36(3), 205-213.
        
    :Parameters:
        * T: air temperature at 2 m [C]
    
    :Returns:
        * Ut: threshold wind speed at 10 m for snow transport [m s-1]
    '''
    a = 9.43 # m s-1
    b = 0.18 # m C-1 s-1
    c = 0.0033 # m C-2 s-1
    
    Ut = a + b*T + c*T**2
    return Ut


def FrictionVelocity(tau0):
    '''
    **Reference:**    
        Gray, D. M., & Male, D. H. (Eds.). (1981). Handbook of Snow. The Blackburn Press. pp. 341
        
    :Parameters:
        * tau0: shear stress at the surface
        
    :Returns:
        * Uf: friction velocity (or sher velocity)
    '''
    Uf = math.sqrt(tau0/rho_air)
    return Uf
    
    
if __name__ == '__main__':
    pass
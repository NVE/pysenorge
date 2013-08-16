__doc_format__ = "reStructuredText"
'''
Functions related to energy transport by radiation.
===================================================

:Author: kmu
:Created: 2. mai 2011
'''

''' Imports '''
# Built-in

# Additional

# Own
from pysenorge.constants import stefan_boltzmann


def EnergyFluxBalance(SWin, SWout, LWin, LWout, Hs, Hl, G=0.0):
    '''
    Energy balance equation for the energy transfer between two volumes using
    incoming and outgoing radiations.
    
    Neglecting horizontal energy transfers as well as effects due to blowing
    snow or vegetation, the balance for an open and flat snow cover is given in
    units W m-2 by:
    
    :Parameters:
        * SWin:  short wave radiation downward
        * SWout: short wave radiation upward
        * LWin:  long wave radiation downward
        * LWout: long wave radiation upward
        * Hs:    sensible heat flux
        * Hl:    latent heat flux
        * G:     Ground heat flux
        
    :Returns:
        * dH:    net change rate of internal energy per unit area
    
    :Note: Downward orientated energy is taken as positive (energy gain).
    
    *Reference:*
        Armstrong, R. L., & Brun, E. (Eds.). (2008). Snow and Climate:
        Physical Processes, Surface Energy Exchange and Modeling (p. 256).
        Cambridge University Press. Pp. 72.
    
    '''
    dH = SWin + SWout + LWin + LWout + Hs + Hl + G
    return dH

def EnergyNetFluxBalance(SWnet, LWnet, Hs, Hl, G=0.0):
    '''
    Energy balance equation for the energy transfer between two volumes using
    net radiation.
    
    Neglecting horizontal energy transfers as well as effects due to blowing
    snow or vegetation, the balance for an open and flat snow cover is given in
    units W m-2 by:
    
    :Parameters:
        * SWnet: net short wave radiation
        * LWnet: net long wave radiation
        * Hs:    sensible heat flux
        * Hl:    latent heat flux
        * G:     Ground heat flux
        
    :Returns:
        * dH:    net change rate of internal energy per unit area
    
    :Note: Downward orientated energy is taken as positive (energy gain).
    
    *Reference:*
        Armstrong, R. L., & Brun, E. (Eds.). (2008). Snow and Climate:
        Physical Processes, Surface Energy Exchange and Modeling (p. 256).
        Cambridge University Press. Pp. 72.
    
    '''
    dH = SWnet + LWnet + Hs + Hl + G
    return dH


def NetRadiation(SWnet, LWnet):
    '''
    :Parameters:
        * SWnet: net short wave radiation
        * LWnet: net long wave radiation
    '''
    Rnet = SWnet + LWnet
    return Rnet


def IncomingLongWave(T, eps=1.0):
    '''
    :Parameters:
        * T:    near-surface air temperature [Celsius]
        * eps:  effective emissivity for the atmosphere - default = 1.0
        
    :Returns:
        * LWin: incoming longwave radiation [W m-2]
    '''
    LWin = - eps * stefan_boltzmann * (T + 273.15)**4
    return LWin


def OutgoingLongWave(T0, LWin, eps=0.98):
    '''
    :Parameters:
        * T0:   surface temperature [Celsius]
        * LWin: incoming longwave radiation [W m-2]
        * eps:  snow infrared emissivity - default = 0.98
        
    :Returns:
        * LWout: outgoing longwave radiation [W m-2]
    '''
    LWout = eps * stefan_boltzmann * (T0+273.15)**4 - (1-eps)*LWin
    return LWout


if __name__ == '__main__':
    pass
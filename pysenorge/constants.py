'''
Contains physical constants used in snow modeling.

@var a_gravity: Gravitational acceleration [m s-2]
@var eta0: Viscosity of snow at T=0C and density=0 [N s m- 2 = kg m-1 s-1]
@var rho_air: Density of air [kg m-3], dry air at 0 C and 100 kPa
@var rho_water: Density of water [kg m-3]
@var rho_ice: Density of ice [kg m-3]
@var k_ice0:  Thermal conductivity of ice [W m-1 K-1] at 0 C
@var k_ice10:  Thermal conductivity of ice [W m-1 K-1] at -10 C
@var secperday: Seconds per day [s]
@var boltzmann: Boltzmann constant [J K-1].
    The Boltzmann constant (k or kB) is the physical constant relating energy
    at the particle level with temperature  observed at the bulk level. 
    It is the gas constant R divided by the Avogadro constant NA: k = \frac{R}{N_{\rm A}}\,
    It has the same units as entropy.
    
@var boltzmann_eV: Boltzmann constant [eV K-1]

@author: kmu
@since: 25. mai 2010
'''

# gravitational acceleration [m s-2]
a_gravity = 9.81

# viscosity of snow at T=0C and density=0 [N s m- 2= kg m-1 s-1]
eta0 = 3.6e6

# Density of air [kg m-3], dry air at 0 C and 100 kPa
rho_air = 1.2754 

# Density of water [kg m-3]  
rho_water = 1000.0

# Density of ice [kg m-3]
rho_ice = 916.0

# Thermal conductivity of ice [W m-1 K-1]
k_ice0 = 2.22 # at 0 C
k_ice10 = 2.30 # at -10 C

# Seconds per day [s]
secperday = 86400.0

# Boltzmann constant [J K-1]
# The Boltzmann constant (k or kB) is the physical constant relating energy
# at the particle level with temperature  observed at the bulk level. 
# It is the gas constant R divided by the Avogadro constant NA:
#    k = \frac{R}{N_{\rm A}}\,
# It has the same units as entropy.
boltzmann = 1.380650424e-23
boltzmann_eV = 8.61734315e-5 # [eV K-1]

# Stefan-Boltzmann constant [W m-2 K-4]
stefan_boltzmann = 5.67040004e-8
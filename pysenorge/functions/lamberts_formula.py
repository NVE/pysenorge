# -*- coding:iso-8859-10 -*-
__docformat__ = 'reStructuredText'
'''
Doc...

:Author: kmu
:Created: 2. mai 2011
'''
# Built-in
import math
# Additional

# Own
def LambertsFormula(N, NE, E, SE, S, SW, W, NW):
    """
    A formula for computing the mean wind-direction from a series of
    observations.
    N, NE, ..., NW are the number of observations in each direction.
    
    **Reference:**
        Heidorn, K.C., "An index to measure consistency of the wind direction for periods around one day", Atmospheric Env. Vol 12, pp 993-996.
    """
    # theta is the angle interval. For a 16-section classification use 22.5 deg.
    theta = math.radians(45)
    Ce = E - W + (NE+SE-NW-SW) * math.cos(theta)
    Cn = N - S + (NE+NW-SE-SW) * math.sin(theta)
    
    # Consistency index Ci    
#    H = N+NE+E+SE+S+SW+W+N
#    Ci = int(100/H * math.sqrt(Cn**2 + Ce**2))
#    print "Ci =", Ci

    # arctan of the ratio Ce/Cn
    alpha = math.atan2(Ce, Cn)
    degalpha = math.degrees(alpha)

    wid={-22.5<=degalpha<22.5:1,#N
         22.5<=degalpha<67.5:2,#NE
         67.5<=degalpha<112.5:3,#E
         112.5<=degalpha<157.5:4,#SE
         157.5<=degalpha<180:5,#S
        -22.5>=degalpha>-67.5:6,#SW
        -67.5>=degalpha>-112.5:7,#W
        -112.5>=degalpha>-157.5:8,#NW
        -157.5>=degalpha>-180:5,#S
        }[1]
    return wid  

    
#     # Translate azimuth to cardinal wind direction
#     if degalpha >= 0.0:
#         if degalpha >=0.0 and degalpha<22.5:
#             # wd = 'N'
#             wid = 1
#         elif degalpha >=22.5 and degalpha<67.5:
#             # wd = 'NE'
#             wid = 2
#         elif degalpha >=67.5 and degalpha<112.5:
#             # wd = 'E' 
#             wid = 3
#         elif degalpha >=112.5 and degalpha<157.5:
#             # wd = 'SE'
#             wid = 4
#         elif degalpha >=157.5 and degalpha<=180.0:
#             # wd = 'S'  
#             wid = 5 
#     if degalpha < 0.0:
#         if degalpha <0.0 and degalpha>=-22.5:
#             # wd = 'N'
#             wid = 1
#         elif degalpha <-22.5 and degalpha>=-67.5:
#             # wd = 'NW'
#             wid = 8
#         elif degalpha <-67.5 and degalpha>=-112.5:
#             # wd = 'W' 
#             wid = 7
#         elif degalpha <-112.5 and degalpha>=-157.5:
#             # wd = 'SW'
#             wid = 6
#         elif degalpha <-157.5 and degalpha>=-180.0:
#             # wd = 'S'  
#             wid = 5
#     return wid

if __name__ == '__main__':
    pass
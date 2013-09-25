'''
Created on 23.09.2013

@author: ralf
'''
#Build in
import math

#Additional 
from numpy import sqrt, mean, zeros_like, arctan2, degrees, amax, where

#OWN
from pysenorge.functions.lamberts_formula import LambertsFormula
from pysenorge.functions.dominant_wind import dom_wind


#---------------------------------------------------------
#Define wind model
#---------------------------------------------------------
def model(x_wind, y_wind):
    """
    Calculates avg. and max. wind speed and prevailing wind direction from the
    x and y vector components.

    :Parameters:
        - x_wind: Wind vector component in *x*-direction
        - y_wind: Wind vector component in *y*-direction
    """

    total_wind = sqrt(x_wind ** 2 + y_wind ** 2)
    dims = total_wind.shape
    total_wind_avg = mean(total_wind, axis=0)
    wind_dir_cat = zeros_like(total_wind_avg)
    wind_dir = arctan2(y_wind, x_wind)
    max_wind = amax(total_wind[0:24, 0:dims[1], 0:dims[2]], axis=0)
    new_wind_dir = degrees(wind_dir)
    print "Wind-data dimensions:", dims

#---------------------------------------------------------
#Create wind direction vector
    for i in xrange(dims[1]):
        for j in xrange(dims[2]):
            N = 0
            NE = 0
            E = 0
            SE = 0
            S = 0
            SW = 0
            W = 0
            NW = 0
            for k in xrange(dims[0]):
                alpha = wind_dir[k, i, j]
                degalpha = math.degrees(alpha)
                if degalpha >= 0.0:
                    if degalpha >= 0.0 and degalpha < 22.5:
                        W += 1
                    elif degalpha >= 22.5 and degalpha < 67.5:
                        SW += 1
                    elif degalpha >= 67.5 and degalpha < 112.5:
                        S += 1
                    elif degalpha >= 112.5 and degalpha < 157.5:
                        SE += 1
                    elif degalpha >= 157.5 and degalpha <= 180.0:
                        E += 1
                if degalpha < 0.0:
                    if degalpha < 0.0 and degalpha >= -22.5:
                        W += 1
                    elif degalpha < -22.5 and degalpha >= - 67.5:
                        NW += 1
                    elif degalpha < -67.5 and degalpha >= -112.5:
                        N += 1
                    elif degalpha < -112.5 and degalpha >= -157.5:
                        NE += 1
                    elif degalpha < -157.5 and degalpha >= -180.0:
                        E += 1

            wind_dir_cat[i][j] = LambertsFormula(N, NE, E, SE, S, SW, W, NW)

    return total_wind_avg, max_wind, total_wind, wind_dir_cat


'''
Created on 10.09.2013

@author: Ralf Loritz
'''

# Built-in
import math
    
def dom_wind(ob_wind_dir_cat,ob_pre_wind,ob_up,ob_low, ob_wind_dir, ob_total_wind,i,j,ob_dom_wind,ob_dims):
    """
    Calculates the maximal wind speed for the dominant wind direction on basis of the Lamberts equation.
    
    *Todo:*
    Change the code to a more efficient vectorized code with for example the numpy module.   
    """
    if ob_wind_dir_cat[i][j] == ob_pre_wind:
        li_new = []
        for k in xrange(ob_dims[0]):
            alpha = ob_wind_dir[k,i,j]
            degalpha = math.degrees(alpha)
            if degalpha < 0:
                if degalpha < ob_up and degalpha >= ob_low:
                    li_new.append(ob_total_wind[k,i,j])  
                    ob_dom_wind[i][j] = max(li_new)
            else:
                if degalpha >= ob_up and degalpha< ob_low:
                    li_new.append(ob_total_wind[k,i,j])  
                    ob_dom_wind[i][j] = max(li_new)
    return ob_dom_wind

if __name__ == '__main__':
    pass
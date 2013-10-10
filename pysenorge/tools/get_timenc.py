'''
Created on 23.09.2013

@author: ralf
'''

#Get timenc
def _time_fun(ob_time):
    if ob_time == "07":
        timenc = "00"
    elif ob_time == "13":
        timenc = "06"
    elif ob_time == "19":
        timenc = "12"
    elif ob_time == "01":
        timenc = "18"

    return timenc


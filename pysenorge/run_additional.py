'''
Created on 02.10.2013

@author: ralf
'''
def main():
    import sys
    import subprocess

    date = sys.argv[1]

    # Run temperatur-gradient-daily
    tmgr = subprocess.Popen(["./themes/temperature_gradient_daily.py", date])
    tmgr.wait()
    # Run temperatur-stability-index
    ssttm = subprocess.Popen(["./themes/temperature_stability_index.py", date])
    ssttm.wait()
    # Additional-snowdepth
    asd = subprocess.Popen(["./themes/additional_snow_depth_wind_vareexp.py", date])
    asd.wait()

print "All scripts where running successfully"

if __name__ == '__main__':
    main()

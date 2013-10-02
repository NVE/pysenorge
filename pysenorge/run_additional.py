'''
Created on 02.10.2013

@author: ralf
'''

import sys
import subprocess

ob_date = sys.argv[1].split("-")
yr = ob_date[0]
mm = ob_date[1]
dd = ob_date[2]

load_date = "%s_%s_%s" % (yr, mm, dd)

#create import_path


# Run temperatur-gradient-daily
tmgr = subprocess.Popen("")
tmgr.wait()
# Run temperatur-stability-index
ssttm = subprocess.Popen("")
ssttm.wait()
# Additional-snowdepth
asd = subprocess.Popen("")
asd.wait()

if __name__ == '__main__':
    pass

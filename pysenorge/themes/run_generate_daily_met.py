__docformat__ = 'reStructuredText'
'''
Script creating the daily met netCDF files (set up in TaskScheduler).

*Author:* kmu
*Created:* 07. jan. 2011
'''
import sys
import os
import logging
import datetime
execfile(os.path.join(os.path.dirname(__file__), "set_pysenorge_path.py"))
from pysenorge.set_environment import LOGdir

print sys.argv

if len(sys.argv) == 1:
    _date = datetime.date.today().isoformat()+"T06:00:00"
elif len(sys.argv) == 2:
    _date = sys.argv[1]+"T06:00:00"
else:
    print "Provide date as YYYY-MM-DD. No argument use today's date."
    sys.exit(1)
    
    

scriptname = "../tools/generate_daily_met.py"

dt = datetime.timedelta(days=1)

LOG_FILENAME = os.path.join(LOGdir,
                            scriptname.split('.')[0]+'.log')
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)

logging.info('Script started: %s' % datetime.datetime.now().isoformat())
print datetime.datetime.now().isoformat()
script = os.path.join(os.path.dirname(__file__), scriptname)
os.system("python %s %s -d %s -i ml -o 0 " % (script,
                                              _date,
                                              r'Z:\metdata\prognosis\um4\2011'))

logging.info('"ml" finished: %s' % datetime.datetime.now().isoformat())

os.system("python %s %s -d %s" % (script,
                                  _date,
                                  r'Z:\metdata\prognosis\um4\2011'))

logging.info('"sf" finished: %s' % datetime.datetime.now().isoformat())
logging.info('Script finished: %s' % datetime.datetime.now().isoformat())
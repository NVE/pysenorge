__docformat__ = 'reStructuredText'
'''
Doc...

:Author: kmu
:Created: 24. april 2010
'''
import os
import logging
from datetime import timedelta, datetime
execfile(os.path.join(os.path.dirname(__file__), "set_pysenorge_path.py"))
from pysenorge.tools.date_converters import iso2datetime

scriptname = "wind_10m_daily.py"

LOG_FILENAME = os.path.join(os.path.expanduser("~"),
                            scriptname.split('.')[0]+'.log')
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)

logging.info('Script started: %s' % datetime.now().isoformat())

start_date = "2011-05-27"
end_date = "2011-06-08"
start_date =  iso2datetime(start_date+"T00:00:00")
end_date =  iso2datetime(end_date+"T00:00:00")

dt = timedelta(days=1)

while start_date < end_date:
    start_date
    strdate = "%s-%s-%s" % (str(start_date.year).zfill(2),
                            str(start_date.month).zfill(2),
                            str(start_date.day).zfill(2))
    script = os.path.join(os.path.dirname(__file__), scriptname)
    os.system("python %s %s" % (script, strdate)) 
    start_date = start_date+dt
    
logging.info('Script finished: %s' % datetime.now().isoformat())
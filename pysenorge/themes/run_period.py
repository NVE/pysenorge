__docformat__ = 'reStructuredText'
'''
Doc...

:Author: kmu
:Created: 13. Sept. 2011
'''
import os
import logging
from datetime import timedelta, datetime
execfile(os.path.join(os.path.dirname(__file__), "set_pysenorge_path.py"))
from pysenorge.tools.date_converters import iso2datetime


def runPeriod(scriptname, start_date, end_date):
    """
    All input as strings
    
    Example input:
    scriptname = "wind_10m_daily.py"
    start_date = "2011-05-27"
    end_date = "2011-06-08"
    """
    
    LOG_FILENAME = os.path.join(os.path.expanduser("~"),
                                scriptname.split('.')[0]+'.log')
    logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)
    
    logging.info('Script started: %s' % datetime.now().isoformat())
    
    start_date =  iso2datetime(start_date+"T00:00:00")
    end_date =  iso2datetime(end_date+"T00:00:00")
    
    dt = timedelta(days=1)
    
    while start_date <= end_date:
        strdate = "%s-%s-%s" % (str(start_date.year).zfill(2),
                                str(start_date.month).zfill(2),
                                str(start_date.day).zfill(2))
        script = os.path.join(os.path.dirname(__file__), scriptname)
        os.system("python %s %s" % (script, strdate)) 
        start_date = start_date+dt
        
    logging.info('Script finished: %s' % datetime.now().isoformat())
    
    
if __name__ == "__main__":
#    runPeriod("wind_10m_daily.py", "2011-01-26", "2011-04-30")
    runPeriod("wind_600m_daily.py", "2011-10-01", "2011-12-14")
    runPeriod("additional_snow_depth_wind.py", "2011-10-01", "2011-12-14")
#    runPeriod("additional_snow_depth_wind600.py", "2011-11-01", "2011-12-14")
#    runPeriod("depth_hoar_index_1.py", "2011-09-01", "2011-10-24")
#    runPeriod("depth_hoar_index_2.py", "2010-09-01", "2011-10-20")
    
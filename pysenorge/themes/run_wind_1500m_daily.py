#! /usr/bin/python
__docformat__ = 'reStructuredText'
'''
Script creating the daily theme (set up in TaskScheduler/crontab).

:Author: kmu
:Created: 01. apr. 2011
'''
import run_daily

run_daily.runDaily("wind_1500m_daily.py", prognosis=True,
                   UMperiod=['[7,12]'])

#
#import os
#import logging
#import datetime
#execfile(os.path.join(os.path.dirname(__file__), "set_pysenorge_path.py"))
#
#
#scriptname = "wind_1500m_daily.py"
#
#dt = datetime.timedelta(days=1)
#
#LOG_FILENAME = os.path.join(os.path.expanduser("~"),
#                            scriptname.split('.')[0]+'.log')
#logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)
#
#logging.info('Script started: %s' % datetime.datetime.now().isoformat())
#
#script = os.path.join(os.path.dirname(__file__), scriptname)
#os.system("python %s %s" % (script,
#                                  (datetime.date.today()-dt).isoformat()))
#os.system("python %s %s" % (script, datetime.date.today().isoformat()))
#os.system("python %s %s -t [7,12]" % (script, datetime.date.today().isoformat()))
#
#logging.info('Script finished: %s' % datetime.datetime.now().isoformat())
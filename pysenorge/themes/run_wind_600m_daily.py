#! /usr/bin/python
__docformat__ = 'reStructuredText'
'''
Script creating the daily theme (set up in TaskScheduler).


*Author:* kmu
*Created:* 20. oct. 2011
'''
import run_daily

run_daily.runDaily("wind_600m_daily.py", prognosis=True,
                   UMperiod=['[7,12]'])
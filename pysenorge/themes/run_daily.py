__docformat__ = 'reStructuredText'
'''
Doc...

:Author: kmu
:Created: 13. Sept. 2011
'''
import os
import logging
import datetime
execfile(os.path.join(os.path.dirname(__file__), "set_pysenorge_path.py"))


def runDaily(scriptname, prognosis=False, UMperiod=['[6,30]']):
    """
    All input as strings - no white spaces! "Bash" doesn't like them very much!
    
    Example input:
    scriptname = "wind_10m_daily.py"
    """

    dt = datetime.timedelta(days=1)
    
    LOG_FILENAME = os.path.join(os.path.expanduser("~"),
                                scriptname.split('.')[0]+'.log')
    logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)
    
    logging.info('Script started: %s' % datetime.datetime.now().isoformat())
    
    script = os.path.join(os.path.dirname(__file__), scriptname)
    os.system("python %s %s" % (script, (datetime.date.today()-dt).isoformat()))
    logging.info("File for %s written!" % (datetime.date.today()-dt).isoformat())
    os.system("python %s %s" % (script, datetime.date.today().isoformat()))
    logging.info("File for %s written!" % datetime.date.today().isoformat())
    if prognosis:
        for period in UMperiod:
            os.system("python %s %s -t %s" % (script,
                                              datetime.date.today().isoformat(),
                                              period))
            logging.info("File for %s written!" % (datetime.date.today()+dt).isoformat())
    
    logging.info('Script finished: %s' % datetime.datetime.now().isoformat())
   
if __name__ == "__main__":
    print "Usage:\nimport run_daily\nrun_daily.runDaily(full_script_name)"
    
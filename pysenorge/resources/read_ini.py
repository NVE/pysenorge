'''
Doc...

@author: kmu
@since: 28. okt. 2010
'''
import os
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('win.ini')

# getfloat() raises an exception if the value is not a float
# getint() and getboolean() also do this for their respective types
METdir = os.path.normpath(config.get('Folders', 'MET_DIR'))
print METdir

UintFillValue = config.getint('Constants', 'UintFillValue')

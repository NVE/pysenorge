__docformat__ = 'reStructuredText'
'''
Sets the *PYseNorge* home directory.

.. note:: This script must be placed under ~/pysenorge/themes/
.. note:: Import in each theme layer script to ensure the PYTHONPATH is set correctly.

:Author: kmu
:Created: 6. sep. 2010
'''
import os, sys

# Add folder containing the "pysenorge" package to the PYTHONPATH
thisdir = os.path.dirname(os.path.abspath(__file__))
basedir = os.path.split(os.path.split(thisdir)[0])[0] # requires this script to be in ~/pysenorge/theme_layers/
if basedir in sys.path:
    pass
else:
    sys.path.append(basedir)
    print '''\nAdded "%s" to PYTHONPATH\n''' % sys.path[-1]
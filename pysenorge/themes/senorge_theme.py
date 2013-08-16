# -*- coding:iso-8859-10 -*-
__docformat__ = 'reStructuredText'
'''
Doc...

:Author: kmu
:Created: 31. mars 2011
'''
# Built-in

# Additional

# Own

class seNorgeTheme(object):
    '''
    The abstract class for seNorge themes.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
    def model(self):
        '''
        The numerical model that generates the theme.
        '''
        pass
    
    def setup(self):
        '''
        Method that setup input and output for the model.
        '''
        pass
    
    def getInput(self):
        pass
    
    def setOutput(self):
        pass
    
    def makeCLT(self):
        '''
        Method that generates the color-lookup-table (clt) for the theme
        '''
        pass
    
    def view(self):
        '''
        Method for plotting the theme based on the CLT settings.
        '''
        pass
    
    def runPeriod(self):
        '''
        Method for generating the theme over a given time period.
        '''
        pass
    
    def runDaily(self):
        '''
        Method that generates the theme on a daily basis.
        '''
        pass
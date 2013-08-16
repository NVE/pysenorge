__doc_format__ = "reStructuredText"
'''
Doc...

:Author: kmu
:Created: 13. mai 2011
'''

''' Imports '''
# Built-in

# Additional
import matplotlib.pyplot as plt
# Own


def Histogram(M, B=30, R=None):
    if R == None:
        plt.hist(M, bins=B)
    else:
        plt.hist(M, bins=B, range=R)
    plt.show()
    

if __name__ == '__main__':
    pass
#!/usr/bin/env python
"""
ASCII command-line progress bar with percentage and elapsed time display

@author: adapted from Pylot source code (original by Vasil Vangelovski)
@change: modified by Corey Goldberg - 2010
@change: kmu, 2010-11-02
"""
import sys

class ProgressBar:
    def __init__(self, duration):
        self.duration = duration
        self.prog_bar = '[]'
        self.fill_char = '='
        self.width = 40
        self.__update_amount(0)
    
    def __update_amount(self, new_amount):
        percent_done = int(round((new_amount / 100.0) * 100.0))
        all_full = self.width - 2
        num_hashes = int(round((percent_done / 100.0) * all_full))
        self.prog_bar = '[' + self.fill_char * num_hashes + ' ' * (all_full - num_hashes) + ']'
        pct_place = (len(self.prog_bar) / 2) - len(str(percent_done))
        pct_string = '%i%%' % percent_done
        self.prog_bar = self.prog_bar[0:pct_place] + \
            (pct_string + self.prog_bar[pct_place + len(pct_string):])
        
    def update(self, elapsed_secs, optinfo=''):
        self.__update_amount((elapsed_secs / float(self.duration)) * 100.0)
#        self.prog_bar += '  %ds/%ss' % (elapsed_secs, self.duration)
        self.prog_bar += ' %s' % optinfo
        sys.stdout.write("%s\r" % self.__str__())
        sys.stdout.flush()
        
    def __str__(self):
        return str(self.prog_bar)
        
        
        
if __name__ == '__main__':
    from time import sleep
    p = ProgressBar(60)
    c = 0
    for i in range(60):
        sleep(0.2)
        c += 1
        p.update(i+1, str(c))
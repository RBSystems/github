#! /usr/bin/env python

'''
check if all jobs have been finished normally
'''

import os
import sys

def check_stats():

    log_file = 'supercell.%02d.out'% 0
    if not os.path.exists(log_file):
        msg = 'supercell.00.out not found.'
        return False, msg
    elif os.path.exists('supercell.%02d.out'% 1):
        msg = 'multiple log files found.'
        return False, msg

    content = os.popen('grep "DONE" %s'% log_file).read()
    if content == "":
        msg = 'Job not completed.'
        return False, msg
    else:
        msg = None
        return True, msg


if __name__ == "__main__":

    pre_pathname = 'supercell'
    i = 1
    width = 3
    print '\n'

    while os.path.isdir('%s-%03d'%(pre_pathname, i)):
        os.chdir('%s-%03d'%(pre_pathname, i))
        check_result = check_stats()
        if not check_result[0]:
            print 'Error at %s-%03d, message is: %s\n'%(pre_pathname, i, check_result[1])
        os.chdir('..')
        i += 1

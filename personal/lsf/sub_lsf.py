#! /usr/bin/env python

'''
submit pbs files for all subdirectories in format supercell-***.
'''

import os
import sys
import re
from math import *

if __name__ == "__main__":

    max_count=101;
    file_pbs = 'lsf.sh'
    file_ignore = ['.*out', '.*log']
    pwd = os.getcwd()
    all_dir = []
    for (dirpath, dirnames, filenames) in os.walk(pwd):
        dirnames.sort()
        all_dir.extend(dirnames)
        break

    count = 0;
    for this_dir in all_dir:
        if count>max_count: break
        work_dir = os.path.join(pwd, this_dir)
        excluded = False
        for this_ignore in file_ignore:
            for this_file in os.listdir(work_dir):
                if re.search(this_ignore, this_file):
                    excluded = True
                    break
        if not excluded:
            #print work_dir
            count += 1;
            os.chdir(work_dir)
            os.system('bsub %s'%(file_pbs))

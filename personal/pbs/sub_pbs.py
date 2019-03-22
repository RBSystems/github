#! /usr/bin/env python

'''
submit pbs files for all subdirectories in format supercell-***.
'''

import os
import sys
from math import *
import numpy as np

if __name__ == "__main__":

    file_pbs = 'pbs.sh'
    pwd = os.getcwd()
    all_dir = []
    for (dirpath, dirnames, filenames) in os.walk(pwd):
        dirnames.sort()
        all_dir.extend(dirnames)
        break

    for this_dir in all_dir:
        work_dir = os.path.join(pwd, this_dir)
        os.chdir(work_dir)
        os.system('qsub %s'%(file_pbs))

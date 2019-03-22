#! /usr/bin/env python

'''
write pbs files for all subdirectories in format disp-***.
'''

import os
import sys
from math import *

if __name__ == "__main__":

    pwd = os.getcwd()
    all_dir = []
    for (dirpath, dirnames, filenames) in os.walk(pwd):
        dirnames.sort()
        all_dir.extend(dirnames)
        break

    file_pbs = 'pbs.sh'

    with open(file_pbs) as f:
        lines = f.readlines()

    for i in range(len(lines)):
        if ('-N' in lines[i]) and ('PBS' in lines[i]):
            pre_name = lines[i].split()[-1]
            line_marked = i

    f = open('pbs.all', 'wb')
    for i in range(len(lines)):
        if 'cd' in lines[i]:
            for this_dir in all_dir:
                work_dir = os.path.join(pwd, this_dir)
                f.write('echo -e "\\\n\n\n')
                f.write('=======================================================\n')
                f.write('Current directory: %s\n'% work_dir) #careful! not tested
                f.write('=======================================================\n')
                f.write('"\n')
                f.write('cd %s\n'% work_dir)
#                f.write("aprun -n 1024 -N 32 -d 1 -cc numa_node /u/sciteam/zhang7/bin/rmg-cpu supercell.in > supercell.out\n")
                f.write('mpirun -np 64 --bind-to none --map-by ppr:32:node:pe=1 /software/user_tools/current/cades-virtues/apps/vasp/intel/5.4.1/cades_opt/vasp_std\n')
                f.write('wait\n\n')
        else:
            f.write(lines[i])

    f.write('date')
    f.close()

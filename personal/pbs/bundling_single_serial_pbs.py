#! /usr/bin/env python

'''
write pbs files for all subdirectories in format disp-***.
'''

import os
import sys
import subprocess

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
        if ('nodes' in lines[i]) and ('PBS' in lines[i]):
            nnodes=int(lines[i].split()[-1].split('=')[1].split(':')[0])

    num_dir = len(all_dir)
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
                f.write('if [ ! -e OUTCAR ]; then\n')
                f.write('mpirun -np %d --bind-to none --map-by ppr:32:node:pe=1 /software/user_tools/current/cades-virtues/apps/vasp/intel/5.4.1/cades_opt/vasp_std\n'%(32*nnodes))
                f.write('wait\n')
                f.write('fi\n\n')
        elif (not 'mpirun' in lines[i]):
            f.write(lines[i])

    f.write('date')
    f.close()

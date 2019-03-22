#! /usr/bin/env python

'''
write pbs files for all subdirectories in format disp-***.
'''

import os
import sys
from math import *


########################################
max_nodes_per_pbs = 64

pbs_header = 'pbs.header'

########################################


pwd = os.getcwd()
all_dir = []
for (dirpath, dirnames, filenames) in os.walk(pwd):
    dirnames.sort()
    all_dir.extend(dirnames)
    break

def getDir(all_dir=all_dir):
    for this_dir in all_dir:
        yield this_dir

n_jobs = len(all_dir)

with open(pbs_header) as f:
    lines = f.readlines()

for i in range(len(lines)):
    if ('-N' in lines[i]) and ('PBS' in lines[i]):
        init_name = lines[i].split()[-1]
        name_marked = i
    elif ('PBS' in lines[i]) and ('nodes' in lines[i]):
        init_nodes = int(lines[i].split('=')[1].split(':')[0])
        nodes_marked = i
    elif 'aprun' in lines[i]:
        aprun_marked = i
        aprun_params = lines[i].split()
        if '-n' in aprun_params:
            aprun_n = int(aprun_params[aprun_params.index('-n')+1])
        if '-N' in aprun_params:
            aprun_N = int(aprun_params[aprun_params.index('-N')+1])
        if '-d' in aprun_params:
            aprun_d = int(aprun_params[aprun_params.index('-d')+1])

# check if parameters are consistent
if (aprun_n != init_nodes*aprun_N) or ( aprun_N*aprun_d != 32):
    print "Error: nodes/aprun settings are wrong, exit.\n"
    sys.exit(1)

# how many jobs per pbs run
n_pbs = divmod(max_nodes_per_pbs, init_nodes)[0]
# calculate how many pbs need
x, y = divmod(n_jobs, n_pbs)

if x == 0:
    f = open('pbs.all', 'wb')

    for i in range(len(lines)):
        if i == name_marked:
            f.write('#PBS -N %s@%s\n'% (init_name, pwd))
        elif i == nodes_marked:
            f.write('#PBS -l nodes=%d:ppn=32:xe\n'% (n_jobs*init_nodes))
        elif 'cd' in lines[i] or 'aprun' in lines[i]:
            continue
        else:
            f.write(lines[i])
    
    for this_dir in all_dir:
        f.write('cd %s\n'% os.path.join(pwd, this_dir))
        f.write('%s &\n\n'% lines[aprun_marked].rstrip())
        #f.write('aprun -n %d -N %d -cc numa_node /u/sciteam/zhang7/bin/rmg-cpu %s > %s &\n'%(aprun_n, aprun_N, ))
    
    f.write('\n\nwait')
    f.close()

else:
    all_dir = iter(all_dir)
    for pbs_index in range(x+1):
        f = open('pbs.all.%d'% pbs_index, 'wb')
        for i in range(len(lines)):
            if i == name_marked:
                f.write('#PBS -N %s-%d@%s\n'% (init_name, pbs_index, pwd))
            elif i == nodes_marked:
                f.write('#PBS -l nodes=%d:ppn=32:xe\n'% (n_pbs*init_nodes))
            elif 'cd' in lines[i] or 'aprun' in lines[i]:
                continue
            else:
                f.write(lines[i])

        for j in range(n_pbs):
            try:
                this_dir = all_dir.next()
                f.write('cd %s\n'% os.path.join(pwd, this_dir))
                f.write('%s &\n\n'% lines[aprun_marked].rstrip())
            except StopIteration:
                break
        #f.write('aprun -n %d -N %d -cc numa_node /u/sciteam/zhang7/bin/rmg-cpu %s > %s &\n'%(aprun_n, aprun_N, ))
    
        f.write('\n\nwait')
        f.close()
    exit()
    # write the left jobs
    f = open('pbs.all.%d'% x, 'wb')
    for i in range(len(lines)):
        if i == name_marked:
            f.write('#PBS -N %s-%d@%s\n'% (init_name, x, pwd))
        elif i == nodes_marked:
            f.write('#PBS -l nodes=%d:ppn=32:xe\n'% (y*init_nodes))
        elif 'cd' in lines[i] or 'aprun' in lines[i]:
            continue
        else:
            f.write(lines[i])

    for j in range(y):
        try:
            all_dir.next()
        except StopIteration:
            break 
        this_dir
        f.write('cd %s\n'% os.path.join(pwd, this_dir))
        f.write('%s &\n\n'% lines[aprun_marked].rstrip())
    #f.write('aprun -n %d -N %d -cc numa_node /u/sciteam/zhang7/bin/rmg-cpu %s > %s &\n'%(aprun_n, aprun_N, ))

    f.write('\n\nwait')
    f.close()

#! /usr/bin/env python

'''
sub all sub-directoreis jobs in jobs bundling way
'''

import os
import sys

pwd = os.getcwd()
all_dir = []
for (dirpath, dirnames, filenames) in os.walk(pwd):
    dirnames.sort()
    all_dir.extend(dirnames)
    break

file_pbs = 'pbs.single'

n_jobs = len(all_dir)

with open(file_pbs) as f:
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

#! /usr/bin/env python

'''
convert qe atomic positions format from others to crystal
'''

import sys
import numpy as np

file_in = 'qe.in.old'
with open(file_in, 'rb') as f:
    lines = f.readlines()

pos = []
celldm = []

# find parameters
for i,line in enumerate(lines):
    if 'nat' in line.lower():
        nat = int(filter(str.isdigit, line))
    if 'celldm' in line.lower():
        tmp = line.replace('=',' ').replace(',', ' ').split()[1]
        celldm.append(float(tmp))
    elif 'cell_parameters' in line.lower():
        celldm.append(float(lines[i+1].split()[0]))
        celldm.append(float(lines[i+2].split()[1]))
        celldm.append(float(lines[i+3].split()[2]))
    if 'atomic_positions' in line.lower():
        if 'crystal' not in line.lower():
            line_atom = i
        else:
            print "Already in crystal type, exit."
            sys.exit(1)

len_dm = len(celldm)
if len_dm == 1:
    celldm = [celldm[0]]*3

for i in range(line_atom+1, line_atom+1+nat):
    tmp_species = lines[i].split()[0]
    tmp_x = float(lines[i].split()[1])/celldm[0]
    tmp_y = float(lines[i].split()[2])/celldm[1]
    tmp_z = float(lines[i].split()[3])/celldm[2]
    pos.append([tmp_species, tmp_x, tmp_y, tmp_z])

# create new parameters
lines_pp = ''
for i in range(len(lines)):
    # skip copy original atom pos
    if i<line_atom+1+nat and i>line_atom:
        continue
    line = lines[i]
    if 'ibrav' in line:
        lines_pp += ' '*4 + 'ibrav = 0\n'
    elif 'celldm' in line:
        if len_dm == 1:
            lines_pp += ' '*4 + 'celldm(1) = %f,\n'% celldm[0]
            lines_pp += ' '*4 + 'celldm(2) = %f,\n'% celldm[1]
            lines_pp += ' '*4 + 'celldm(3) = %f,\n'% celldm[2]
        else:
            if 'celldm(1)' in line:
                lines_pp += ' '*4 + 'celldm(1) = %f,\n'% celldm[0]
            if 'celldm(2)' in line:
                lines_pp += ' '*4 + 'celldm(2) = %f,\n'% celldm[1]
            if 'celldm(3)' in line:
                lines_pp += ' '*4 + 'celldm(3) = %f,\n'% celldm[2]
    elif 'atomic_positions' in line.lower():
        lines_pp += 'ATOMIC_POSITIONS crystal\n'
        for j in range(nat):
            pos_tmp = pos[j][0], pos[j][1], pos[j][2], pos[j][3]
            lines_pp += '%s\t%15.9f%15.9f%15.9f\n'%(pos_tmp)
    else:
        lines_pp += line

with open('qe.in', 'wb') as f:
    f.write(lines_pp)

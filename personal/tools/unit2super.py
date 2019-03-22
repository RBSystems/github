#! /usr/bin/env python

'''
build supercells from unit cell for RMG
'''

import os
import sys

dim = [3, 3, 1]

prefix = sys.argv[-1]

with open('%s'%(prefix), 'rb') as f:
    all_lines = f.readlines()

relative = False
factor = [1.0]*3
species, x, y, z = [], [], [], []
for i in range(len(all_lines)):
    if "Cell Relative" in all_lines[i].split('#')[0]:
        relative = True

for i in range(len(all_lines)):
    if "a_length" in all_lines[i]:
        a_length = float(all_lines[i].split('"')[1])
        if relative:
            factor[0] = a_length
    if "b_length" in all_lines[i]:
        b_length = float(all_lines[i].split('"')[1])
        if relative:
            factor[1] = b_length
    if "c_length" in all_lines[i]:
        c_length = float(all_lines[i].split('"')[1])
        if relative:
            factor[2] = c_length
    if "atoms =" in all_lines[i]:
        for j in range(i+2,len(all_lines)-1):
            species.append(str(all_lines[j].split()[0]))
            x.append(factor[0]*float(all_lines[j].split()[1]))
            y.append(factor[1]*float(all_lines[j].split()[2]))
            z.append(factor[2]*float(all_lines[j].split()[3]))


lines_super = ""
for line in all_lines:
    if "a_length" in line:
        line = 'a_length="%.12f"\n'%(dim[0]*a_length)
    if "b_length" in line:
        line = 'b_length="%.12f"\n'%(dim[1]*b_length)
    if "c_length" in line:
        line = 'c_length="%.12f"\n'%(dim[2]*c_length)
    lines_super += line
    if 'atoms' in line.split('#')[0]:
        break

if '"' not in lines_super[-1]:
    lines_super += '"\n'


for i in range(dim[0]):
    for j in range(dim[1]):
        for k in range(dim[2]):
            for n in range(len(x)):
                atom_tmp = (species[n],
                            i*a_length+x[n],
                            j*b_length+y[n],
                            k*c_length+z[n])
                lines_super += '%s%18.12f%18.12f%18.12f\n'%(atom_tmp)
lines_super += '"'

with open("%s.super"% prefix, 'wb') as f:
    f.write(lines_super)

#!/usr/bin/env python

import math
import random
import numpy as np

orig_input = "rmg.in.orig"
pert_input = "rmg.in"

with open(orig_input, 'rb') as f:
    all_lines = f.readlines()

lines = ""
for i in range(len(all_lines)):
    this_line = all_lines[i]
    if "atoms" not in this_line:
        lines += this_line
    else:
        atoms_line = i
        break

#print lines
atom_name = []
pos = []
for i in range(atoms_line+2, len(all_lines)):
    line_list = all_lines[i].split()
    if len(line_list) < 3:
        break
    atom_name.append(line_list[0])
    pos.append(map(float, line_list[1:4]))

n_atom = len(pos)

theta = 0.5*math.pi*np.random.rand(n_atom)
phi = math.pi*np.random.rand(n_atom)

mag = 0.0001 #angstrom

delta_x = np.multiply(np.sin(theta), np.cos(phi))
delta_y = np.multiply(np.sin(theta), np.sin(phi))
delta_z = np.cos(theta)

delta_all = mag*np.stack((delta_x, delta_y, delta_z)).T

print delta_all[0]
new_pos = np.add(pos, delta_all)

lines += "atoms=\n"
lines += '"\n'
for i in range(n_atom):
    lines += "%2s%20.16f%20.16f%20.16f%4d\n"%(atom_name[i], new_pos[i][0], new_pos[i][1], new_pos[i][2], 1)
lines += '"\n'

with open(pert_input, 'wb') as f:
    f.write(lines)

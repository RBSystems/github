#! /usr/bin/env python

"""
    extract atoms information from RMG log files and convert to XYZ format
"""

import os
import sys

nat = 276
atoms = []
bohr2angstrom = 0.529177249

with open('rmg.in.00.log', 'rb') as f:
    log_lines = f.readlines()

for i in range(len(log_lines)-1, 0, -1):
    if 'IONIC POSITIONS' in log_lines[i]:
        final_pos_line = i
        break

for i in range(final_pos_line+4, final_pos_line+4+nat):
    this_atom = log_lines[i].split()[2:6]
    atoms.append(this_atom)

xyz_lines = ""
xyz_lines += "%d\n"% nat
xyz_lines += "relaxed structure of silica glass surface\n"
for i in range(nat):
    atoms[i][1] = float(atoms[i][1])*bohr2angstrom
    atoms[i][2] = float(atoms[i][2])*bohr2angstrom
    atoms[i][3] = float(atoms[i][3])*bohr2angstrom
    xyz_lines += '%4s%16.8f%16.8f%16.8f\n'% tuple(atoms[i])

with open('relaxed.xyz', 'wb') as f:
    f.write(xyz_lines)

exit()

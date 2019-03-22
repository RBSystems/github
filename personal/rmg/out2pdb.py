#! /usr/bin/env python

"""
    extract atoms information from RMG log files and convert to PDB format
"""

import os
import sys

atoms = []
bohr2angstrom = 0.529177249

if len(sys.argv) > 1:
    log_file = sys.argv[-1]
else:
    log_file = "rmg.in.00.log"
    print "No input log file, default %s will be used.\n"% log_file

with open(log_file, 'rb') as f:
    log_lines = f.readlines()

# find number of atoms
for i in range(len(log_lines)):
    if "Number of ions" in log_lines[i]:
        nat = int(log_lines[i].split()[-1])
        break


# find lattice constants
for i in range(len(log_lines)):
    if "Basis Vector" in log_lines[i]:
        latvec_line = i
        break

lat_x = float(log_lines[i].split()[3])   
lat_y = float(log_lines[i+1].split()[4])   
lat_z = float(log_lines[i+2].split()[5])   

# find all ionic positions
for i in range(len(log_lines)-1, 0, -1):
    if 'IONIC POSITIONS' in log_lines[i]:
        final_pos_line = i
        break

for i in range(final_pos_line+4, final_pos_line+4+nat):
    this_atom = log_lines[i].split()[2:6]
    atoms.append(this_atom)

pdb_lines = ""
pdb_lines += "%5s%1d%9.3f%9.3f%9.3f%7.2f%7.2f%7.2f%2s%2d%12d\n"%(
            "CRYST", 1, lat_x*bohr2angstrom, lat_y*bohr2angstrom, lat_z*bohr2angstrom,
            90, 90, 90, 'P', 1, 1)

#pdb_lines += "relaxed structure of silica glass surface\n"
for i in range(nat):
    atoms[i][1] = float(atoms[i][1])*bohr2angstrom
    atoms[i][2] = float(atoms[i][2])*bohr2angstrom
    atoms[i][3] = float(atoms[i][3])*bohr2angstrom
    pdb_lines += "%4s%7d%4s%7s%4d    %8.3f%8.3f%8.3f%6.2f%6.2f        %4s\n"%(
        'ATOM', i+1, atoms[i][0], 'X', 1, atoms[i][1], atoms[i][2], atoms[i][3],
        0.0 , 0.0, atoms[i][0].upper())

with open('relaxed.pdb', 'wb') as f:
    f.write(pdb_lines)

exit()

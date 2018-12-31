#! /usr/bin/env python
'''
    description:
        automatic scripts for frozen phonon calculations
    input:
        YAML file
        VASP input files
    output:
        VASP input files with displacements for frozen phonon calculations
'''

import os
import sys
import copy
import math
import yaml
import shutil
import numpy as np

#===========================================
# Basic settings
#===========================================
#displacement range
disp_min = 0.0
disp_max = 2.0
disp_fine_limit = 1.0
disp_step = 0.04
disp_step_fine = 0.02


#===========================================
# Main program
#===========================================
#check vasp input files
vasp_inp = ['KPOINTS', 'POTCAR', 'INCAR']
for i in vasp_inp:
    if not os.path.isfile(i):
        print("Error: %s not found."%i)
        sys.exit(1)

#check basename
if len(sys.argv) > 1:
    basename = sys.argv[1]
else:
    print('Error: a base name must be provided.\n')
    sys.exit(1)

yamlfile = basename.split('.')[0]+'.yaml'

# set up displacements
disp_0 = np.arange(-disp_max, -disp_fine_limit, disp_step)
disp_1 = np.arange(-disp_fine_limit, disp_fine_limit, disp_step_fine)
disp_2 = np.arange(disp_fine_limit, disp_max+0.0001, disp_step)
disp = np.append(disp_0, np.append(disp_1, disp_2))

#read YAML file
yamlout = yaml.load(open(yamlfile))

# find mass
denorm_mat = [[math.sqrt(x['mass'])] for x in yamlout['atoms']]

# read lattice vectors
lat_x, lat_y, lat_z = yamlout['lattice']

# read atoms positions
atoms = yamlout['atoms']
atoms_pos = []
for i in range(yamlout['natom']):
    atoms_pos.append(np.dot(atoms[i]['coordinates'][0],lat_x) +
                     np.dot(atoms[i]['coordinates'][1],lat_y) +
                     np.dot(atoms[i]['coordinates'][2],lat_z)
)

# read freq & eigvec at Gamma point
for i in range(len(yamlout['phonon'])):
    if np.linalg.norm(yamlout['phonon'][i]['q-position']) < 1.0e-6:
        index_gamma = i
        break

phonon = yamlout['phonon'][index_gamma]
eigvec = []
for i in range(len(phonon['band'])):
    eigvec.append([])
    for j in range(len(yamlout['atoms'])):
        eigvec[-1].append([])
        eigvec[-1][-1].append(phonon['band'][i]['eigenvector'][j][0][0])
        eigvec[-1][-1].append(phonon['band'][i]['eigenvector'][j][1][0])
        eigvec[-1][-1].append(phonon['band'][i]['eigenvector'][j][2][0])

atoms_disp = []
for i in range(len(yamlout['phonon'][0]['band'])):
    atoms_disp.append(copy.deepcopy(atoms_pos))

# denormalized displacement
eigvec_denorm = np.divide(eigvec, denorm_mat)

# count unique name of symbols
symbol = []
count = []
for i in range(yamlout['natom']):
    if yamlout['atoms'][i]['symbol'] not in symbol:
        symbol.append(yamlout['atoms'][i]['symbol'])
        count.append(1)
    else:
        count[-1] = count[-1] + 1

for i in range(len(yamlout['phonon'][0]['band'])):
    if not os.path.exists('freq@%f_#%d'% (yamlout['phonon'][index_gamma]['band'][i]['frequency'], i+1)):
        os.makedirs('freq@%f_#%d'% (yamlout['phonon'][index_gamma]['band'][i]['frequency'], i+1))
    for this_disp in disp:
        file_path = os.path.join('freq@%f_#%d'% (yamlout['phonon'][index_gamma]['band'][i]['frequency'], i+1), 'disp@%f'% this_disp)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        # copy KPOINTS, POTCAR, INCAR
        shutil.copyfile("INCAR", os.path.join(file_path, "INCAR"))
        shutil.copyfile("KPOINTS", os.path.join(file_path, "KPOINTS"))
        shutil.copyfile("POTCAR", os.path.join(file_path, "POTCAR"))

        file_name = os.path.join(file_path, 'POSCAR')
        pos_lines = ""
        pos_lines += "%s frozen phonon calculation\n"%(basename)
        pos_lines += "1.0\n"
        pos_lines += "    %12.6f%12.6f%12.6f\n"%tuple(lat_x)
        pos_lines += "    %12.6f%12.6f%12.6f\n"%tuple(lat_y)
        pos_lines += "    %12.6f%12.6f%12.6f\n"%tuple(lat_z)
        pos_lines += "   "
        for j in range(len(symbol)):
            pos_lines += " %s"%symbol[j]
        pos_lines += "\n"
        for j in range(len(symbol)):
            pos_lines += "%d "%count[j]
        pos_lines += '\n'
        pos_lines += "Cart\n"
        for j in range(yamlout['natom']):
            this_disp_vec = np.array(eigvec_denorm[i][j])*this_disp
            atoms_disp[i][j] = np.array(atoms_pos[j]) + this_disp_vec

            # write positions files
            pos_lines += "    %12.8f%12.8f%12.8f\n"%(atoms_disp[i][j][0], atoms_disp[i][j][1], atoms_disp[i][j][2])
        pos_lines += '\n'

        with open(file_name, 'wb') as f:
            f.write(pos_lines)

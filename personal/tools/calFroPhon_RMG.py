#! /usr/bin/env python

import os
import copy
import numpy as np

disp_0 = np.arange(-0.5, -0.2, 0.01)
disp_1 = np.arange(-0.2, 0.2, 0.001)
disp_2 = np.arange(0.2, 0.51, 0.01)

disp = np.append(disp_0, np.append(disp_1, disp_2))

with open('rmg.mesh.yaml') as f:
    all_lines = f.readlines()

# read lattice vectors
for i in range(len(all_lines)):
    if "lattice" in all_lines[i] and "reciprocal" not in all_lines[i]:
        lat_x = float(all_lines[i+1].split()[2].split(',')[0])
        lat_y = float(all_lines[i+2].split()[3].split(',')[0])
        lat_z = float(all_lines[i+3].split()[4].split(',')[0])
        break

# read atoms positions
atoms = []
for i in range(len(all_lines)):
    if "atoms" in all_lines[i]:
        for j in range(i, len(all_lines)):
            if "symbol" in all_lines[j]:
                atoms.append([])
                atoms[-1].append(all_lines[j].split()[2])
                atoms[-1].append([])
                atoms[-1][-1].append(lat_x*float(all_lines[j+1].split()[2].split(',')[0]))
                atoms[-1][-1].append(lat_y*float(all_lines[j+1].split()[3].split(',')[0]))
                atoms[-1][-1].append(lat_z*float(all_lines[j+1].split()[4].split(',')[0]))
            if "phonon" in all_lines[j+1]: break
        break;

print atoms[-1][-1]

# read freq & eigvec
freq, freq_index, eigvec = [], [], []
for i in range(len(all_lines)):
    if 'q-position: [    0.0000000,    0.0000000,    0.0000000 ]' in all_lines[i]:
        line_gamma = i
        break

for i in range(line_gamma, len(all_lines)):
    if 'frequency' in all_lines[i]:
        freq.append(float(all_lines[i].split()[1]))
        freq_index.append(int(all_lines[i-1].split('#')[-1]))
        eigvec.append([])
        for j in range(i, len(all_lines)):
            if "atom" in all_lines[j]:
                eigvec[-1].append([])
                eigvec[-1][-1].append(float(all_lines[j+1].split()[2].split(',')[0]))
                eigvec[-1][-1].append(float(all_lines[j+2].split()[2].split(',')[0]))
                eigvec[-1][-1].append(float(all_lines[j+3].split()[2].split(',')[0]))
            if 'frequency' in all_lines[j+1]:
                break

    if 'q-position' in all_lines[i+1]:
        break

#atoms_disp = [copy.deepcopy(atoms)]*len(freq)
atoms_disp = []
for i in range(len(freq)):
    atoms_disp.append(copy.deepcopy(atoms))

# read rmg header
with open('rmg.in.header', 'rb') as f:
    head_lines = f.read()

for i in range(len(freq)):
    if not os.path.exists('freq@%f_#%d'% (freq[i], freq_index[i])):
        os.makedirs('freq@%f_#%d'% (freq[i], freq_index[i]))
    for this_disp in disp:
        file_path = os.path.join('freq@%f_#%d'% (freq[i], freq_index[i]), 'disp@%f'% this_disp)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        file_name = os.path.join(file_path, 'rmg.in')
        pos_lines = ""
        pos_lines += head_lines
        pos_lines += "atoms=\n"
        pos_lines += '"\n'
        for j in range(len(atoms)):
            this_disp_vec = np.array(eigvec[i][j])*this_disp
            atoms_disp[i][j][1] = np.array(atoms[j][1]) + this_disp_vec

            # write positions files
            pos_lines += "%4s%12.8f%12.8f%12.8f\n"%(atoms_disp[i][j][0], atoms_disp[i][j][1][0], atoms_disp[i][j][1][1], atoms_disp[i][j][1][2])
        pos_lines += '"\n'

        with open(file_name, 'wb') as f:
            f.write(pos_lines)

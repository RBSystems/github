#!/usr/bin/env python
'''
    now considers about degree of freedom
'''

import os
import sys
import numpy as np
from ase.io import read

mode = 'lammps'
kB = 8.6173303e-5 #Boltzmann constant
T = 300.00# Kelvin
beta_inv = kB*T

if mode == 'vasp':
    cell = read('POSCAR', format="vasp")
    #trajs = read('XDATCAR', format="vasp-xdatcar", index=":10")
    trajs = read('XDATCAR', format="vasp-xdatcar", index=":")
elif mode == 'lammps':
    cell = read('Si222.lammps', format='lammps-data', style='atomic')
    trajs = read('silicon.lammpstrj.100000',index=":", format='lammps-dump', order=False)

n_atom = len(cell.positions)

GF_mat = np.zeros((3*n_atom, 3*n_atom))

#define traj_ix and traj_jy
traj_mat = np.zeros((n_atom, 3, len(trajs)))
#mean_1d = np.zeros((n_atom, 3))
#mean_2d = np.zeros((n_atom, ))
for i in range(n_atom):
    for x in range(3):
        traj_mat[i][x] = [trajs[k][i].position[x] for k in range(len(trajs))]
mean_1d = np.mean(traj_mat, axis=2)
#mean_2d = np.mean(np.matmul(traj_mat,traj_mat))
for i in range(n_atom):
    for j in range(n_atom):
        tmp_mat = np.zeros((3,3))
        for x in range(3):
            for y in range(3):
                tmp = np.mean(np.multiply(traj_mat[i][x],traj_mat[j][y])) - mean_1d[i][x]*mean_1d[j][y]
                #phi_tmp = beta_inv/tmp
                tmp_mat[x][y] = tmp
        inv_tmp = np.linalg.inv(tmp_mat)
        GF_mat[3*i:3*i+3,3*j:3*j+3] = inv_tmp

FC_mat = beta_inv*GF_mat*n_atom/len(trajs)

#nasr=10
#impose ASR and symmetry; could be done via phonopy
#for x in range(nasr):
#    # asr
#    for i in range(n_atom):
#        for x in range(3):
#            for y in range(3):
#                tmp = 0.0
#                for j in range(n_atom):
#                    if j!=i:
#                        tmp += FC_mat[3*i+x][3*j+y]
#                FC_mat[3*i+x][3*i+y] = -tmp
#
#    # symmetry
#    FC_mat = (FC_mat + FC_mat.T)/2.0

lines = "%d %d\n"%(n_atom, n_atom)
lines_GF = "%d %d\n"%(n_atom, n_atom)
for i in range(n_atom):
    for j in range(n_atom):
        lines += "%8d%8d\n"%(i+1, j+1)
        lines_GF += "%8d%8d\n"%(i+1, j+1)
        for x in range(3):
            for y in range(3):
                lines += "%22.16f"%FC_mat[3*i+x][3*j+y]
                lines_GF += "%22.16f"%GF_mat[3*i+x][3*j+y]
            lines += "\n"
            lines_GF += "\n"

with open("FORCE_CONSTANTS", 'wb') as f:
    f.write(lines)

with open("GF_MAT", 'wb') as f:
    f.write(lines_GF)

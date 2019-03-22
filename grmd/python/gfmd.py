#!/usr/bin/env python

import os
import sys
import numpy as np
from ase.io import read


kB = 8.6173303e-5 #Boltzmann constant
T = 300.00# Kelvin
beta_inv = kB*T

cell = read('POSCAR', format="vasp")

n_atom = len(cell.positions)
#trajs = read('XDATCAR', format="vasp-xdatcar", index=":10")
trajs = read('XDATCAR', format="vasp-xdatcar", index=":")

GF_mat = np.zeros((3*n_atom, 3*n_atom))
for i in range(n_atom):
    for j in range(n_atom):
        # <delta_a*delta_b> = <ab> - <a><b>
        for x in range(3):
            traj_i = [trajs[k][i].position[x] for k in range(len(trajs))]
            for y in range(3):
                traj_j = [trajs[k][j].position[y] for k in range(len(trajs))]
                tmp = np.mean(np.multiply(traj_i,traj_j)) - np.mean(traj_i)*np.mean(traj_j)
                #phi_tmp = beta_inv/tmp
                GF_mat[3*i+x][3*j+y] = tmp

FC_mat = beta_inv*np.linalg.inv(GF_mat)

#impose ASR
for i in range(n_atom):
    for x in range(3):
        for y in range(3):
            tmp = 0.0
            for j in range(n_atom):
                if j!=i:
                    tmp += FC_mat[3*i+x][3*j+y]
            FC_mat[3*i+x][3*i+y] = -tmp

lines = "%d %d\n"%(n_atom, n_atom)
for i in range(n_atom):
    for j in range(n_atom):
        lines += "%8d%8d\n"%(i+1, j+1)
        for x in range(3):
            for y in range(3):
                lines += "%22.16f"%FC_mat[3*i+x][3*j+y]
            lines += "\n"

with open("FORCE_CONSTANTS", 'wb') as f:
    f.write(lines)

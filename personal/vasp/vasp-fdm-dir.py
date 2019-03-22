#! /usr/bin/env python

'''
    mv all POSCAR-??? files to a new created disps directories, and
    copy other inputs files to the all subdirectries

    TODO: use shell to program this function
'''

import os
import sys
from shutil import copy, move

other_inp = ['INCAR', 'KPOINTS', 'POTCAR']

n_disp = 1
while True:
    if os.path.isfile('POSCAR-%03d'% n_disp):
        n_disp += 1
    else:
        break

if not os.path.isdir('disps'):
    os.mkdir('disps')

for i in range(n_disp):
    ''' disps-000 to store perfect supercell without perturbations'''
    crt_dir = 'disps'+'/'+'disp-%03d'%i
    if not os.path.isdir(crt_dir):
        os.mkdir(crt_dir)
    for _file in other_inp:
        copy(_file, crt_dir)
    if i != 0:
        copy('POSCAR-%03d'%i, crt_dir+'/'+'POSCAR')
    else:
        copy('SPOSCAR', crt_dir+'/'+'POSCAR')

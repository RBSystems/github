#
# CASTEP.py
#
# Interface to Quantum ESPRESSO (http://www.quantum-espresso.org)
#
# Copyright (c) 2018 Jiayong Zhang
#
# This file is distributed under the terms of the MIT license.
# Please see the file 'LICENCE.txt' in the root directory
# or http://opensource.org/licenses/mit-license.php for information.
#

import os
import numpy as np

def read_castep_input(file_in):

    format_geom = False
    format_cell = False
    if "cell" in file_in:
        format_cell = True
    elif "geom" in file_in:
        format_geom = True


    with open(file_in, 'rb') as f:
        lines_inp = f.readlines()

    latvec = np.zeros((3, 3))
    Eng2Ryd = 1.0
    length2angst = 0.5291772108
    atom_name, atom_pos = [], []

    if format_geom:
        for i in range(len(lines_inp)):
            this_line = lines_inp[i].split('#')[0]
            if " E" in this_line and "<" in this_line:
                latvec[0] = map(float, lines_inp[i+1].split()[0:3])
                latvec[1] = map(float, lines_inp[i+2].split()[0:3])
                latvec[2] = map(float, lines_inp[i+3].split()[0:3])
                #latvec[0] = np.dot(length2angst, map(float, lines_inp[i+1].split()[0:3]))
                #latvec[1] = np.dot(length2angst, map(float, lines_inp[i+2].split()[0:3]))
                #latvec[2] = np.dot(length2angst, map(float, lines_inp[i+3].split()[0:3]))
                break
    elif format_cell:
        for i in range(len(lines_inp)):
            this_line = lines_inp[i].split('#')[0]
            # be careful of the units here
            if "lattice_cart" in this_line.lower():
                latvec[0] = np.divide(map(float, lines_inp[i+1].split()[0:3]), length2angst)
                latvec[1] = np.divide(map(float, lines_inp[i+2].split()[0:3]), length2angst)
                latvec[2] = np.divide(map(float, lines_inp[i+3].split()[0:3]), length2angst)
                break

    invlatvec = np.linalg.inv(latvec)

    if format_geom:
        for i in range(len(lines_inp)):
            this_line = lines_inp[i].split('#')[0]
            if "R" in this_line and "<" in this_line:
                this_line_spl = this_line.split('#')[0].split()
                if len(this_line_spl) < 2:
                    continue
                atom_name.append(this_line_spl[0])
                atom_pos.append(np.dot(map(float, this_line_spl[2:5]), invlatvec))
    elif format_cell:
        for i in range(len(lines_inp)):
            this_line = lines_inp[i].split('#')[0]
            if "positions_frac" in this_line.lower():
                for j in range(i+1, len(lines_inp)):
                    this_line_spl = lines_inp[j].split()
                    if len(this_line_spl) != 4:
                        break
                    atom_name.append(this_line_spl[0])
                    atom_pos.append(map(float, this_line_spl[1:4]))

    if not os.path.exists('orig.pos.rel.dat'):
        np.savetxt('orig.pos.rel.dat', atom_pos, fmt="%18.10f")
    latvec *= length2angst
    elements = np.unique(atom_name)

    return latvec, elements, len(atom_name), atom_pos

# castep may exceeds 1.0
def refold(x):
#    if x > 1.0:
#        x -= np.floor(x)
#    elif x < -1.0:
#        x -= np.ceil(x)

    if x >= 0.5:
        return x - 1.0
    elif x < -0.5:
        return x + 1.0
    else:
        return x

def print_displacements_CASTEP(log_files,
                           lavec, nat, x0,
                           require_conversion,
                           conversion_factor,
                           file_offset):

    import math
    Bohr_to_angstrom = 0.5291772108
    vec_refold = np.vectorize(refold)

    x0 = np.round(x0, 8)

    lavec /= Bohr_to_angstrom
    invlavec = np.linalg.inv(lavec)
    #print lavec; exit()
    lavec_transpose = lavec.transpose()
    lavec_transpose_inv = np.linalg.inv(lavec_transpose)

    if file_offset is None:
        disp_offset = np.zeros((nat, 3))
    else:
        x0_offset = get_coordinates_CASTEP(file_offset, nat)
        try:
            x0_offset = np.reshape(x0_offset, (nat, 3))
        except:
            print("File %s contains too many position entries" % file_offset)
            exit(1)
        disp_offset = x0_offset - x0

    for search_target in log_files:

        x = get_coordinates_CASTEP(search_target, nat)

        ndata = len(x) // (3 * nat)
        x = np.reshape(x, (ndata, nat, 3))

        for idata in range(ndata):
            disp = np.dot(x[idata, :, :], invlavec) - x0 - disp_offset
            #print disp;exit()
            disp = np.dot(vec_refold(disp), lavec_transpose)
            for i in range(nat):
                print("%15.7F %15.7F %15.7F" % (disp[i, 0],
                                                disp[i, 1],
                                                disp[i, 2]))

def get_coordinates_CASTEP(log_file, nat):

    search_flag = " T"

    x = []
    skip_line = 3

    f = open(log_file, 'r')
    line = f.readline()

    # Search other entries containing atomic position
    while line:
        if search_flag in line:
            # skip useless lines
            for j in range(skip_line):
                line = f.readline()
            for i in range(nat):
                line = f.readline()
                x.extend([tmp for tmp in line.rstrip().split()[2:5]])
        line = f.readline()
    f.close()

    return np.array(x, dtype=np.float)


def get_atomicforces_CASTEP(log_file, nat):

    search_flag = " T"

    f = open(log_file, 'r')
    line = f.readline()

    skip_line = 3+nat*2
    force = []

    while line:
        if search_flag in line:
            # skip useless lines
            for j in range(skip_line):
                line = f.readline()
            for i in range(nat):
                line = f.readline()
                force.extend([tmp for tmp in line.rstrip().split()[2:5]])
        line = f.readline()
    f.close()

    return np.array(force, dtype=np.float)

def print_atomicforces_CASTEP(str_files,
                          nat,
                          require_conversion,
                          conversion_factor,
                          file_offset):

    if file_offset is None:
        force_offset = np.zeros((nat, 3))
    else:
        data0 = get_atomicforces_CASTEP(file_offset, nat)
        try:
            force_offset = np.reshape(data0, (nat, 3))
        except:
            print("File %s contains too many force entries" % file_offset)

    for search_target in str_files:

        force = get_atomicforces_CASTEP(search_target, nat)
        ndata = len(force) // (3 * nat)
        force = np.reshape(force, (ndata, nat, 3))

        for idata in range(ndata):
            f = force[idata, :, :] - force_offset

            if require_conversion:
                f *= conversion_factor

            for i in range(nat):
                print("%19.11E %19.11E %19.11E" % (f[i][0],
                                                   f[i][1],
                                                   f[i][2]))


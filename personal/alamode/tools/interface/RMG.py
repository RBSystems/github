#
# RMG.py
#
# Interface to Quantum ESPRESSO (http://www.quantum-espresso.org)
#
# Copyright (c) 2018 Jiayong Zhang
#
# This file is distributed under the terms of the MIT license.
# Please see the file 'LICENCE.txt' in the root directory
# or http://opensource.org/licenses/mit-license.php for information.
#

import numpy as np

def read_rmg_input(file_in):

    with open(file_in, 'rb') as f:
        lines_inp = f.readlines()

    latvec = np.zeros((3, 3))
    Eng2Ryd = 1.0
    length2angst = 1.0
    pos2rel = 1.0
    atom_name, atom_pos = [], []
    
    for i in range(len(lines_inp)):
        this_line = lines_inp[i].split('#')[0]
        if "crds_units" in this_line:
            units = this_line.split('"')[1]
            if units.lower() == "bohr":
                length2angst = 0.5291772108

    for i in range(len(lines_inp)):
        this_line = lines_inp[i].split('#')[0]
        if "a_length" in this_line:
            #latvec[0][0] = length2angst*float(this_line.split('"')[1])
            latvec[0][0] = float(this_line.split('"')[1])
        elif "b_length" in this_line:
            #latvec[1][1] = length2angst*float(this_line.split('"')[1])
            latvec[1][1] = float(this_line.split('"')[1])
        elif "c_length" in this_line:
            #latvec[2][2] = length2angst*float(this_line.split('"')[1])
            latvec[2][2] = float(this_line.split('"')[1])

    for i in range(len(lines_inp)):
        this_line = lines_inp[i].split('#')[0]
        if "atomic_coordinate_type" in this_line:
            if this_line.split('"')[1].lower() == 'absolute':
                pos2rel = np.diag(latvec)

    for i in range(len(lines_inp)):
        this_line = lines_inp[i].split('#')[0]
        if "atoms" in this_line:
            for j in range(i+1, len(lines_inp)):
                this_line_spl = lines_inp[j].split('#')[0].split()
                if len(this_line_spl) < 2:
                    continue
                atom_name.append(this_line_spl[0])
                atom_pos.append(np.divide(map(float, this_line_spl[1:4]), pos2rel))


    latvec *= length2angst
    elements = np.unique(atom_name)

    return latvec, elements, len(atom_name), atom_pos

def refold(x):
    if x >= 0.5:
        return x - 1.0
    elif x < -0.5:
        return x + 1.0
    else:
        return x

def print_displacements_RMG(log_files,
                           lavec, nat, x0,
                           require_conversion,
                           conversion_factor,
                           file_offset):

    import math
    Bohr_to_angstrom = 0.5291772108
    vec_refold = np.vectorize(refold)

    x0 = np.round(x0, 8)

    lavec /= Bohr_to_angstrom
    #print lavec; exit()
    lavec_transpose = lavec.transpose()
    lavec_transpose_inv = np.linalg.inv(lavec_transpose)


    if file_offset is None:
        disp_offset = np.zeros((nat, 3))
    else:
        x_offset = get_coordinates_RMG(file_offset, nat)
        if ndata_offset > 1:
            print("File %s contains too many position entries" % file_offset)
            exit(1)
        else:
            x_offset = alat * np.dot(x_offset, lavec_transpose_inv)
            disp_offset = x_offset - x0

    for search_target in log_files:

        x = get_coordinates_RMG(search_target, nat)
        #x = alat * np.dot(x, lavec_transpose_inv)

        ndata = len(x) // (3 * nat)
        x = np.reshape(x, (ndata, nat, 3))

        for idata in range(ndata):
            disp = np.divide(x[idata, :, :], np.diag(lavec)) - x0 - disp_offset
            disp = np.dot(vec_refold(disp), lavec_transpose)
            for i in range(nat):
                print("%15.7F %15.7F %15.7F" % (disp[i, 0],
                                                disp[i, 1],
                                                disp[i, 2]))

def get_coordinates_RMG(log_file, nat):

    search_flag = "IONIC POSITIONS"

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
                x.extend([tmp for tmp in line.rstrip().split()[3:6]])
        line = f.readline()
    f.close()

    return np.array(x, dtype=np.float)


def get_atomicforces_RMG(log_file, nat):

    search_flag = "IONIC POSITIONS"

    f = open(log_file, 'r')
    line = f.readline()

    skip_line = 3
    force = []

    while line:
        if search_flag in line:
            # skip useless lines
            for j in range(skip_line):
                line = f.readline()
            for i in range(nat):
                line = f.readline()
                force.extend([tmp for tmp in line.rstrip().split()[7:10]])
        line = f.readline()
    f.close()

    return np.array(force, dtype=np.float)

def print_atomicforces_RMG(str_files,
                          nat,
                          require_conversion,
                          conversion_factor,
                          file_offset):

    if file_offset is None:
        force_offset = np.zeros((nat, 3))
    else:
        data0 = get_atomicforces_RMG(file_offset, nat)
        try:
            force_offset = np.reshape(data0, (nat, 3))
        except:
            print("File %s contains too many force entries" % file_offset)

    for search_target in str_files:

        force = get_atomicforces_RMG(search_target, nat)
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


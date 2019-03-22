#! /usr/bin/env python
'''
    usage:
        convert phonopy yaml format to alamode bands foramt
    TODO
'''


import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams.update({'font.size': 30})

band_vasp = "wnac.yaml"
bohr2angst = 0.529177
output = "wnac.bands"
thz2kayser = 33.35641
kpt_rescale_factor = 1.0

# read band.yaml
def read_band_yaml(file):
    with open(file, 'rb') as f:
        lines = f.readlines()

    x, y, kpt = [], [], []
    for i in range(len(lines)):
        if 'q-position' in lines[i]:
            x.append([])
            x[-1].append(kpt_rescale_factor*float(lines[i+1].split()[1]))
            if 'label' in lines[i+2]:
                kpt.append([])
                x[-1].append(lines[i+2].split("'")[1])
                kpt[-1].append(lines[i+2].split("'")[1])
                kpt[-1].append(float(lines[i+1].split()[-1]))
            y.append([])
            for j in range(i+1, len(lines)):
                if 'frequency' in lines[j]:
                    y[-1].append(thz2kayser*float(lines[j].split()[1]))
                elif 'q-position' in lines[j]:
                    break
    return x, y, kpt


kpt_vasp, dos_vasp, kpt = read_band_yaml(band_vasp)

print kpt_vasp[0]

with open(output, 'wb') as f:
    #for i in range(len(kpt_vasp)):
    #    if len(kpt_vasp[i]) > 1:
    #        print 'ha'
    #        f.write(kpt_vasp[i][1])

    # write header
    f.write("#")
    for i in range(len(kpt)):
        f.write(" %s" %kpt[i][0])
    f.write('\n')
    f.write("#")
    for i in range(len(kpt)):
        f.write(" %8.6f" %kpt[i][1])
    f.write('\n')
    f.write('# k-axis, Eigenvalues [cm^-1]\n')

    for i in range(len(kpt_vasp)):
        f.write("%8.6f" %kpt_vasp[i][0])
        for j in range(len(dos_vasp[0])):
            f.write("%15.6e" % dos_vasp[i][j])
        f.write("\n")

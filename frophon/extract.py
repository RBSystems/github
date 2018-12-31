#! /usr/bin/env python

'''
write pbs files for all subdirectories in format disp-***.
todo:
    change disp, energy back to energy; array is disgusting here!!!
'''

import os
import sys
import copy
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import leastsq

def polyfit(x, y, degree):
    results = {}
    coeffs = np.polyfit(x, y, degree)
    results['polynomial'] = coeffs.tolist()

    # r-squared
    p = np.poly1d(coeffs)
    # fit values, and mean
    yhat = p(x)                         # or [p(z) for z in x]
    ybar = np.sum(y)/len(y)          # or sum(y)/len(y)
    ssreg = np.sum((yhat-ybar)**2)   # or sum([ (yihat - ybar)**2 for yihat in yhat])
    sstot = np.sum((y - ybar)**2)    # or sum([ (yi - ybar)**2 for yi in y])
    results['determination'] = ssreg / sstot
    return results

#define
def func(disp, p):
    a = p
    return a*disp**2

def residuals(p, E, disp):
    return E - func(disp ,p)



if __name__ == "__main__":

    file_pbs = 'OUTCAR'
    parent_dir = os.getcwd()
    all_dir = []
    for (dirpath, dirnames, filenames) in os.walk(parent_dir):
        dirnames.sort()
        all_dir.extend(dirnames)
        break

    disp_unsorted = []
    for this_dir in all_dir:
        disp_unsorted.append(float(this_dir.split('@')[-1]))
    disp_index = np.argsort(disp_unsorted)

    all_dir = np.array(all_dir)[disp_index]

    fitting_disp = np.arange(3.0)
    #fitting_disp = np.arange(0.10, 0.16, 0.01)

    disp, energy = np.array([]), np.array([])

    # find all energy
    for this_dir in all_dir:
        work_dir = os.path.join(parent_dir, this_dir)
        this_disp = float(this_dir.split('@')[-1])
        if abs(this_disp) > 2.0:
            continue
        disp = np.append(disp, this_disp)
        energy_found = False
        f = open('%s/%s'%(work_dir, file_pbs),'rb')
        all_lines = f.readlines()
        for line in all_lines[::-1]:
            if 'energy without entropy' in line:
                energy_found = True
                energy = np.append(energy, float(line.split()[-1]))
                break

        if energy_found is False:
            print "WARNING: energy not found at %s, will ignore this item.\n"% this_dir
            disp = np.delete(disp, -1)
            fitting_flag.pop()

        if abs(this_disp) < 0.0001:
            energy_0 = energy[-1]

    # substract the energy at disp=0
    energy = energy - energy_0

    # fitting curve
    for fitting_max in fitting_disp:
        fitting_flag = []
        for this_disp in disp:
            if abs(this_disp) > fitting_max:
                fitting_flag.append(False)
            else:
                fitting_flag.append(True)
    
        fitting_flag = np.array(fitting_flag, dtype=bool)

        # dump disp & energy
        data = zip(disp[fitting_flag], energy[fitting_flag])
        np.savetxt('pes.dat', data, header="Potential energy profile for ***\nDisplacement(angstrom) Energy(eV)")

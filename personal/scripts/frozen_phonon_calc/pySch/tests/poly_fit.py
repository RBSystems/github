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

#define order function
def func(disp, p):
    order = 2*len(p)
    if order == 2:
        a2 = p
        return a2*disp**2
    elif order == 4:
        a4, a2 = p
        return a4*disp**4 + a2*disp**2
    elif order == 6:
        a6, a4, a2 = p
        return a6*disp**6 + a4*disp**4 + a2*disp**2
    elif order == 8:
        a8, a6, a4, a2 = p
        return a8*disp**8 + a6*disp**6 + a4*disp**4 + a2*disp**2
    elif order == 10:
        a10, a8, a6, a4, a2 = p
        return a10*disp**10 + a8*disp**8 + a6*disp**6 + a4*disp**4 + a2*disp**2
    else:
        print("Error: wrong order %d."%order)
        sys.exit(1)

def residuals(p, E, disp):
    return E - func(disp ,p)

if __name__ == "__main__":

    disp, energy = np.array([]), np.array([])

    data = np.genfromtxt("pes.fdm.8.dat")
    disp = zip(*data)[0]
    energy = zip(*data)[1]

    energy_0 = 0.0
    for i in range(len(data)):
        if abs(data[i][0]) < 1.0e-6:
            energy_0 = data[i][1]

    # substract the energy at disp=0
    energy = energy - energy_0



    energy_unit = 'eV'
    disp_unit = 'angstrom'

    target_mass = 1.008
    ev2hartree = 0.0367493
    angstrom2bohr = 1.8897259886

    eigvec_4 = 0.69224167726530

    disp_frac = eigvec_4/np.sqrt(target_mass) # amplitude of target polar vector
    #disp_frac = 0.6817265/np.sqrt(target_mass) # amplitude of target polar vector
    #energy_frac = 0.4647510208
    energy_frac = eigvec_4**2 # for band 8

    energy = energy_frac*ev2hartree*np.array(energy)
    disp = disp_frac*angstrom2bohr*np.array(disp)

    plt.plot(disp, energy, 'k', linewidth='4', label='Original')
    fitting_disp = disp_frac*angstrom2bohr*np.array([2.0])
    # fitting curve
    for fitting_max in fitting_disp:
        fitting_flag = []
        for this_disp in disp:
            if abs(this_disp) > fitting_max:
                fitting_flag.append(False)
            else:
                fitting_flag.append(True)
    
        fitting_flag = np.array(fitting_flag, dtype=bool)

        for this_order in [2, 4, 6, 8, 10]:
            p0 = [1.0]*(this_order/2)
            plsq = leastsq(residuals, p0, args=(energy[fitting_flag], disp[fitting_flag]))
            error = np.linalg.norm(energy - func(disp, plsq[0]))
            print "Current order: %d\n"% this_order,
            print '\nFiting coefficients: ',
            print plsq
            print 'Fiting errors ',
            print 2.0*error/(np.linalg.norm(energy)+np.linalg.norm(func(disp, plsq[0])))
            #fit_param = np.polyfit(disp[fitting_flag], energy[fitting_flag], 2)
            #print 'Fiting coefficients: %f, %f, %f\n'% tuple(fit_param)
            #energy_fit = fit_param[0]*disp**2 + fit_param[1]*disp + fit_param[2]
            plt.plot(disp, func(disp, plsq[0]), label="Fitting order: %d"%this_order)
    #plt.xlim(-.2, 0.2)
    plt.xlabel('Displacement(Bohr)')
    plt.ylabel('Energy(Hartree)')
    plt.legend(loc=0)
    plt.show()

    exit()

    # fitting curve
    for fitting_max in fitting_disp:
        fitting_flag = []
        for this_disp in disp:
            if abs(this_disp) > fitting_max:
                fitting_flag.append(False)
            else:
                fitting_flag.append(True)
    
        fitting_flag = np.array(fitting_flag, dtype=bool)

        p0 = 3.0
        plsq = leastsq(residuals, p0, args=(energy[fitting_flag], disp[fitting_flag]))
        print 'Fiting coefficients: %f\n'% plsq[0]
        #fit_param = np.polyfit(disp[fitting_flag], energy[fitting_flag], 2)
        #print 'Fiting coefficients: %f, %f, %f\n'% tuple(fit_param)
        #energy_fit = fit_param[0]*disp**2 + fit_param[1]*disp + fit_param[2]
        plt.plot(disp, func(disp, plsq[0]), label="Fitting max: %f"%fitting_max)
    #plt.xlim(-.2, 0.2)
    plt.xlabel('Displacement(angstrom)')
    plt.ylabel('Energy(eV)')
    plt.legend()
    plt.show()

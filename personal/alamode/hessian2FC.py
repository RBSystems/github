#!/usr/bin/env python

'''
    the output unit for force is: ev/angstrom^2
'''


import numpy as np



hessianfile = "NaH.hessian"
outputfile = "FORCE_CONSTANTS_from_tdep"

bohr_over_angstrom = 0.529177
eV_over_Ryd = 0.0734986176
factor2phonopy = 1.0/(bohr_over_angstrom**2)/eV_over_Ryd

data = np.loadtxt(hessianfile, skiprows=1)

natom = int(np.max(zip(*data)[0]))
natom2 = natom**2
fc_new = np.multiply(zip(*data)[-1], factor2phonopy)

lines = ""
lines += "%6d %6d\n"%(natom, natom)
for i in range(natom):
    for j in range(natom):
        lines += "   %5d   %5d\n"%(i+1, j+1)
        for x in range(3):
            for y in range(3):
                lines += "   %20.16f"%(fc_new[natom*3*3*i+3*j+natom*3*x+y])
            lines += '\n'
                #lines += "%   %20.16f   %20.16f   %20.16f\n"%(fc_new[natom2*i+natom*j+0], fc_new[natom2*i+atom*j+1], fc_new[natom2*i+natom*j+2])

with open(outputfile, 'wb') as f:
    f.write(lines)

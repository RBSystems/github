#! /usr/bin/env python

'''
Program: determine the best PE settings for RMG
Input:  a, b, c
        kpoint_mesh: kx, ky, kz
        Anstrom or Bohr
Output: Kpoint_mesh
        processor_grid
'''

import numpy as np


units = 'A'

a = 5.725
b = 7.772
c = 19.182

kx = 3
ky = 3
kz = 1

lat = [a, b, c]
lat_sort = np.sort(lat)

if units.lower()=='a' or units.lower()=='angstrom':
    factor = 0.52917721067
elif units.lower()=='b' or units.lower()=='bohr':
    factor = 1.0
else:
    print 'error'
    sys.exit(1)

frac = [lat[i]/lat[0] for i in range(1, 3)]

for i in range(1,100):
    pe_base = 4.0*i
    spacing = lat[0]/(pe_base*factor)
    message = ('Spacing:%10.6f, PEs: [%6.2f, %6.2f, %6.2f], PE/4: [%6.2f, %6.2f, %6.2f]\n'
                %(spacing, pe_base, frac[0]*pe_base, frac[1]*pe_base, i, frac[0]*i, frac[1]*i))
    print message

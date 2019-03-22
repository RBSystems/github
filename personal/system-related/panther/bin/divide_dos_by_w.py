#!/usr/bin/python2

import os
import sys
import matplotlib.pyplot as plt

with open('total_dos.dat') as f:
    lines = f.readlines()
f.close()

freq = []
dos = []
wdos = []

for i in range(1, len(lines)):
    freq.append(float(lines[i].split()[0]))
    dos.append(float(lines[i].split()[1]))

for i in range(len(dos)):
    if freq[i] > 0: 
        wdos.append(dos[i]/freq[i])
    else:
        wdos.append(0)

plt.plot(freq,wdos)
plt.xlabel('Wavenumber/$cm^{-1}$')
plt.ylabel('Intensity')
plt.xlim(0,1000)
plt.grid(True)
plt.savefig('dos_divided_by_w')
plt.show()

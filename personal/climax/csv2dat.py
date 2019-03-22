#!/usr/bin/python

import sys
import numpy as np

energy, dos = [], []
csvfile = sys.argv[-1]

#data = np.loadtxt(csvfile, skiprows=3, delimiter=' ', comments='#')

#print data


#exit()
cm2mev = 0.12398
with open(csvfile, 'rb') as f:
    all_lines = f.readlines()

for line in all_lines:
    if line.split('#')[0] == ' ':
        continue

    energy.append(cm2mev*float(line.split()[0].rstrip(',')))
    dos.append(float(line.split()[1].rstrip(',')))

datfile = csvfile.split('.')[0]+'.dat'
with open(datfile, 'wb') as f:
    f.write("# X Y E\n")
    f.write('\n')
    for i in range(len(energy)):
        f.write('%12.8f %12.8f %12.8f\n' %(energy[i], dos[i], 0.0))

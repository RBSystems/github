#! /usr/bin/env python

'''
to plot band structure and dos togenther
'''

import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams.update({'font.size': 30})

# read band.yaml
def read_band_yaml(file):
    with open(file, 'rb') as f:
        lines = f.readlines()

    x, y = [], []
    for i in range(len(lines)):
        if 'q-position' in lines[i]:
            x.append([])
            x[-1].append(float(lines[i+1].split()[1]))
            if 'label' in lines[i+2]:
                x[-1].append(lines[i+2].split("'")[1])
            y.append([])
            for j in range(i+1, len(lines)):
                if 'frequency' in lines[j]:
                    y[-1].append(float(lines[j].split()[1]))
                elif 'q-position' in lines[j]:
                    break
    return x, y

band_file = "band.yaml"
data_dos = np.loadtxt('total_dos.dat')

data_kpt, data_freq = read_band_yaml(band_file)
#print data_vision[2]


kpt = zip(*data_kpt)[0]
freq = zip(*data_freq)
dos = zip(*data_dos)
ticks = [[], []]
for tmp in data_kpt:
    if len(tmp) == 2:
        ticks[0].append(tmp[0])
        if '\\' in tmp[1]:
            tmp[1] = '$%s$'% tmp[1]
        ticks[1].append(tmp[1])

# Two subplots, unpack the axes array immediately
f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
for i in range(len(freq)):
    ax1.plot(kpt, freq[i], 'b', linewidth='1')
ax1.set_xlabel('KPoint')
ax1.set_ylabel('Frequency(THz)')
ax1.set_xticks(ticks[0], ticks[1])
#ax1.set_title('Sharing Y axis')
ax2.plot(dos[1], dos[0], 'r', linewidth='1')
ax2.set_xlabel('Density of states')
f.title("Band-DOS")
plt.show()
exit()

plt.subplots(1,1)
for i in range(len(y1)-1):
    plt.plot(x1, y1[i], 'b', linewidth='1')
plt.plot(x1, y1[-1], 'b', linewidth='1', label="Quantum Espresso")

for i in range(len(y1)-1):
    plt.plot(x2, y2[i], 'r', linewidth='1')
plt.plot(x2, y2[-1], 'r', linewidth='1', label="RMG")

plt.xlim(0, max(x1))
#plt.ylim(0, 50)
plt.xlabel('kpoint')
plt.ylabel('Frequency(THz)')
plt.legend(loc=(0.6, 0.6))
#plt.savefig('comparison_ammonia.png', dpi=200)
plt.show()

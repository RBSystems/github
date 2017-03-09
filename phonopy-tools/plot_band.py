#! /usr/bin/env python

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

band_qe = "band_qe.yaml"
band_rmg = "band_rmg.yaml"

kpt_qe, dos_qe = read_band_yaml(band_qe)
kpt_rmg, dos_rmg = read_band_yaml(band_rmg)
#print data_vision[2]

x1 = zip(*kpt_qe)[0]
x2 = zip(*kpt_rmg)[0]
y1 = zip(*dos_qe)
y2 = zip(*dos_rmg)
ticks = [[], []]
for tmp in kpt_qe:
    if len(tmp) == 2:
        ticks[0].append(tmp[0])
        if '\\' in tmp[1]:
            tmp[1] = '$%s$'% tmp[1]
        ticks[1].append(tmp[1])

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
plt.xticks(ticks[0], ticks[1])
plt.legend(loc=(0.6, 0.6))
plt.title("Band comparison between RMG and Quantum Espresso")
#plt.savefig('comparison_ammonia.png', dpi=200)
plt.show()

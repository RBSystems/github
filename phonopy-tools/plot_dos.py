#! /usr/bin/env python

import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams.update({'font.size': 30})

dos_qe = zip(*np.loadtxt('dos_qe.dat'))
dos_rmg = zip(*np.loadtxt('dos_rmg.dat'))

plt.subplots(1,1)
plt.plot(dos_qe[0], dos_qe[1], 'b', linewidth='2', label="Quantum Espresso")
plt.plot(dos_rmg[0], dos_rmg[1], 'r', linewidth='2', label="RMG")

#plt.xlim(0, max(x1))
#plt.ylim(0, 50)
plt.xlabel('Frequency(THz)')
plt.ylabel('DOS')
plt.legend(loc=0)
plt.title("DOS comparison between RMG and Quantum Espresso")
#plt.savefig('comparison_ammonia.png', dpi=200)
plt.show()

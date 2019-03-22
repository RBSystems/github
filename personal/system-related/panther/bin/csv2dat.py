#!/usr/bin/env python

import numpy as np

cm2mev = 0.12398

def read_csv(csvfile):
    return np.genfromtxt(('%s'%(csvfile)), delimiter=',', dtype=None)
    #return np.loadtxt(open('%s'%(csvfile),'rb'), delimiter=',')

data = read_csv('out_vis_inc_0K.csv')
x = np.array(map(float, zip(*data)[0]))*cm2mev
y = map(float, zip(*data)[1])

lines = ""
lines += "# X   Y   E\n"
lines += "\n"
#lines += '\n'.join(map(str, zip(x,y))).replace('(', '').replace(')', '').replace(',','')
for i in range(len(x)):
    lines += "%12.7f%12.7f\n"%(x[i], y[i])

with open('out.dat', 'wb') as f:
    f.write(lines)

#! /usr/bin/env python

'''
generate pdb files from RMG input files
'''

import os
import sys

if __name__=="__main__":

    prefix = sys.argv[-1]
    f = open('%s'%(prefix))
    all_lines = f.readlines()
    f.close()
    relative = False
    factor = [1.0]*3
    species, x, y, z = [], [], [], []
    for i in range(len(all_lines)):
        if "Cell Relative" in all_lines[i].split('#')[0]:
            relative = True

    for i in range(len(all_lines)):
        if "a_length" in all_lines[i]:
            a_length = float(all_lines[i].split('"')[1])
            if relative:
                factor[0] = a_length
        if "b_length" in all_lines[i]:
            b_length = float(all_lines[i].split('"')[1])
            if relative:
                factor[1] = b_length
        if "c_length" in all_lines[i]:
            c_length = float(all_lines[i].split('"')[1])
            if relative:
                factor[2] = c_length
        if "atoms =" in all_lines[i]:
            for j in range(i+2,len(all_lines)-1):
                species.append(str(all_lines[j].split()[0]))
                x.append(factor[0]*float(all_lines[j].split()[1]))
                y.append(factor[1]*float(all_lines[j].split()[2]))
                z.append(factor[2]*float(all_lines[j].split()[3]))
    f = open('%s.pdb'%(prefix),'w')
    f.write('%5s%1d%9.3f%9.3f%9.3f%7.2f%7.2f%7.2f%2s%2d%12d\n'%(
            'CRYST',1,a_length,b_length,c_length,90.0,90.0,90.0,'P',1,1))
    for i in range(len(x)):
        f.write('%4s%7d%4s%7s%4d    %8.3f%8.3f%8.3f%6.2f%6.2f        %4s\n'%
                ('ATOM',i+1,species[i],'X',1,x[i],y[i],z[i],1.0,0.0,species[i].upper()))
    f.write('END')
    f.close()

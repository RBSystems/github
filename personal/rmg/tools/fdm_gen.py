#!/usr/bin/python2

#rmg main part: create all input files, for silicon we just need 3

import os
import sys
import time
from math import *
import pylab as pl
import numpy as np

if __name__ == "__main__":

    start = time.time()
    prefix = 'in.ab'
    disp = 0.02
    n = 0 #number of total atoms
#    n_cal = 1 #number of atoms you want to calculate
    delta_lst = [-disp,disp]   #change of positions,should be ~ 0.1
    species = [] #species of atoms
    x,y,z = [],[],[] #positions of all atoms for initial 
    movable = []

#read the input file, and then save initial positions
    f_old = open('../pre/v2/log_no_disp/444/%s'%(prefix))
    all_lines_old = f_old.readlines()
    f_old.close()
    n_lines = len(all_lines_old)

    for i in range(n_lines-1,-1,-1):
        if 'atoms' in all_lines_old[i]:
            line_atoms = i #save the line number of "atoms"
            for j in range(i+1,n_lines-1): #neglect the last line, "
                if (len(all_lines_old[j].split()) == 5):
                    n += 1
                    species.append(all_lines_old[j].split()[0])
                    x.append(float(all_lines_old[j].split()[1]))
                    y.append(float(all_lines_old[j].split()[2]))
                    z.append(float(all_lines_old[j].split()[3]))
                    movable.append(int(all_lines_old[j].split()[-1]))
            break

    n_cal = 16 # number of atoms to be displaced

#create all input files
    for i_delta in range(2):
        delta = delta_lst[i_delta]
        for i in range(n_cal):
#change x
            f_1 = open('./input/%s.%d.%d'%(prefix,i_delta,3*i+0),'w')
            for j in range(line_atoms+2): #write file before positions of atoms
                f_1.write(all_lines_old[j])
            for j in range(n):
                if j==i: #change the position of ith atom
                    f_1.write('%s%12.7f%12.7f%12.7f%5d\n'%(species[j],x[j]+delta,y[j],z[j],movable[j]))
                else:
                    f_1.write('%s%12.7f%12.7f%12.7f%5d\n'%(species[j],x[j],y[j],z[j],movable[j]))
            f_1.write ('"')
            f_1.close()
#change y
            f_2 = open('./input/%s.%d.%d'%(prefix,i_delta,3*i+1),'w')
            for j in range(line_atoms+2):
                f_2.write(all_lines_old[j])
            for j in range(n):
                if j==i:
                    f_2.write('%s%12.7f%12.7f%12.7f%5d\n'%(species[j],x[j],y[j]+delta,z[j],movable[j]))
                else:
                    f_2.write('%s%12.7f%12.7f%12.7f%5d\n'%(species[j],x[j],y[j],z[j],movable[j]))
            f_2.write ('"')
            f_2.close()
#change z
            f_3 = open('./input/%s.%d.%d'%(prefix,i_delta,3*i+2),'w')
            for j in range(line_atoms+2):
                f_3.write(all_lines_old[j])
            for j in range(n):
                if j==i:
                    f_3.write('%s%12.7f%12.7f%12.7f%5d\n'%(species[j],x[j],y[j],z[j]+delta,movable[j]))
                else:
                    f_3.write('%s%12.7f%12.7f%12.7f%5d\n'%(species[j],x[j],y[j],z[j],movable[j]))
            f_3.write ('"')
            f_3.close()

#show time
    end = time.time()
    print ("RMG main part done, total time: %f Seconds\n"%(end-start))

#!/usr/bin/python2

#Pre_rmg part: relax the input file, then rewrite input script,
#including positions, calculation mode, states occupation, wavefunction grid and kpoint mesh

# rewrite input file after relaxed

import os
import sys
import pylab
import time
from math import *
from numpy import *

if __name__ == "__main__":

    prefix = 'in.ab' # name of input file
    n_box = 1 #define n*n*n in a box

#read and save the original input file
    n_atoms = 0 #the number of atoms
    f = open('./%s'%(prefix)) 
    all_lines = f.readlines()
    f.close()

    n_lines = len(all_lines)

    for i in range(n_lines):
        if 'atoms' in all_lines[i]:
            line_atoms = i #record the line of "atoms"

    for j in range(line_atoms,n_lines,1):
#        print len(all_lines_old[j].split())
        if (len(all_lines[j].split()) == 5):
            n_atoms += 1

    species, x, y, z, movable = [], [], [], [], []
    f_new = open('rmg.in','w')
    #read logfile, and save positions
    f_log = open("./%s.00.log"%(prefix))
    all_lines_log = f_log.readlines()
    f_log.close()

    for i in range(len(all_lines_log)):
        if "movable" in all_lines_log[i]:
            line_mv = i
        if "Basis" in all_lines_log[i]:
            a_length = float(all_lines_log[i+1].split()[2])
            b_length = float(all_lines_log[i+2].split()[3])
            c_length = float(all_lines_log[i+3].split()[4])

    for i in range(n_atoms):
        species.append(all_lines_log[line_mv+i+1].split()[2])
        x.append(float(all_lines_log[line_mv+i+1].split()[4]))
        y.append(float(all_lines_log[line_mv+i+1].split()[5]))
        z.append(float(all_lines_log[line_mv+i+1].split()[6]))
        movable.append(int(all_lines_log[line_mv+i+1].split()[-1]))

#create new input file, and run rmg, save new total energy
    for i in range(line_atoms+2):
        if ("wavefunction" not in all_lines[i]) and\
           ("kpoint" not in all_lines[i]) and\
           ("_length" not in all_lines[i]) and\
           ("states_count" not in all_lines[i]) and\
           ("Relax Structure" not in all_lines[i]) and\
           ("Cell Relative" not in all_lines[i]):

            f_new.write(all_lines[i])


        elif "wavefunction" in all_lines[i]:
            f_new.write('''%s"%2d %2d %2d"\n'''%(all_lines[i].split('"')[0],\
                        int(all_lines[i].split('"')[1].split()[0])*n_box,\
                        int(all_lines[i].split('"')[1].split()[1])*n_box,\
                        int(all_lines[i].split('"')[1].split()[2])*n_box))

        elif "kpoint" in all_lines[i]:
            f_new.write('''%s"%2d %2d %2d"\n'''%(all_lines[i].split('"')[0],\
                        int(int(all_lines[i].split('"')[1].split()[0])/n_box),\
                        int(int(all_lines[i].split('"')[1].split()[1])/n_box),\
                        int(int(all_lines[i].split('"')[1].split()[2])/n_box)))

        elif "a_length" in all_lines[i]:
            f_new.write('''%s"%7.4f"\n'''%(all_lines[i].split('"')[0],\
                        a_length*n_box))

        elif "b_length" in all_lines[i]:
            f_new.write('''%s"%7.4f"\n'''%(all_lines[i].split('"')[0],\
                        b_length*n_box))

        elif "c_length" in all_lines[i]:
            f_new.write('''%s"%7.4f"\n'''%(all_lines[i].split('"')[0],\
                        c_length*n_box))

        elif "states_count" in all_lines[i]:
            f_new.write('''%s"%2d %2.1f %2d %2.1f"\n'''%(all_lines[i].split('"')[0],\
                        (n_box**3)*int(all_lines[i].split('"')[1].split()[0]),\
                        float(all_lines[i].split('"')[1].split()[1]),\
                        (n_box**3)*int(all_lines[i].split('"')[1].split()[2]),\
                        float(all_lines[i].split('"')[1].split()[3])))

        elif "Relax Structure" in all_lines[i]:
            f_new.write('''%s"Quench Electrons"\n'''%(all_lines[i].split('"')[0]))

    for ix in range(n_box):
        for iy in range(n_box):
            for iz in range(n_box):
                for j in range(n_atoms):
                    f_new.write('%s%12.7f%12.7f%12.7f%5d\n'%(species[j],\
                                ix*a_length+x[j],\
                                iy*b_length+y[j],\
                                iz*c_length+z[j],movable[j]))
 
    for k in range(line_atoms+n_atoms+2,n_lines):
        f_new.write(all_lines[k])
    f_new.close()


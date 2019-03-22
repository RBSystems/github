#!/usr/bin/python2

#part of phonon, to find the proper lattice constant; this part find energy
#ATTENTION: the coordinate type of input file MUST be RELATIVE

import os
import sys
from math import *
import pylab as pl
import numpy as np
from scipy.optimize import leastsq

def find_erg(prefix):
    f_find = open(prefix)
    find_flag = 0
    all_lines_find = f_find.readlines()
    f_find.close
    for i in range(len(all_lines_find)):
        if 'final total energy' in all_lines_find[i]:
            result = (float(all_lines_find[i].split()[-2]))
            find_flag = 1
            break
    if find_flag == 0:
        print("Error finding final energy!")
    return result

#define
def func(v,p): 
    E0, B0, B0_p, v0 = p
    return (E0 + B0*v*((v0/v)**B0_p/(B0_p - 1) + 1)/B0_p - (v0*B0)/(B0_p - 1))

def residuals(p,E,v):
    return E - func(v,p)

if __name__ == "__main__":

#    os.system('''test -e $1 && echo "The fileprefix '$1' DO NOT EXIST" && exit 0''')
   # if len(sys.argv) == 1:
  #      print 'Please the input file name(WITHOUT .log.*)'
 #       prefix = raw_input()
#    else:
    prefix = sys.argv[-1]
#    while ((os.path.exists(r'%s.*.log.00'%(prefix)))==0):
 #      print ("\nThe filename '%s' DOES NOT EXIST!\n\nInput a new filename:"%(prefix)),
  #     prefix = raw_input()

#    x = np.linspace(10.1701,10.3592,5) #displacement
    x = np.array([10.1701, 10.217375, 10.264650, 10.2667])
    v = .25*x**3
#    for i in range(len(x)):
 #       v.append(0.25*(x[i]**3))
  #  print v
    n = len(x)
    E = np.array([-38.291668, -38.294069, -38.295670, -38.295729]) #save all the history total energy
#    os.syste"rm -f rmg.log %s.?.*"%prefix))
#    f_save = open('lat.dat','a')
#    os.system('mpirun -np 6 ~/chips/rmg-release1.2.0/rmg in.c6h6')

#find the initial total energy
#    E_ini = find_erg("%s.log.00"%(prefix))
 #   print ("e.initial found: %f\n"%(E_ini))

#create new input file, and run rmg, save new total energy
#    for i in range(n):
#        E.append(find_erg("%s.%d.log.00"%(prefix,i)))
#        print ('e[%d] found: %f\n'%(i,E[i]))
##        e[i] -= e_ini
#        f_save.write('%f %f\n'%(x[i],E[i]))
#    f_save.close()

#plot
#    pylab.plot(x,e,'bo')
#    pylab.xlabel('Distance/Bohr')
#    pylab.ylabel('Energy/Ha')
#    pylab.grid(True)
#    pylab.savefig('Energy')
#    p.show()
#
#fit the curve by Murnaghan equation
    p0 = [-40.0, 100.0, 100.0, 270.0]
    plsq = leastsq(residuals, p0, args=(E, v))

    pl.plot(v, E, label=u"samples")
    pl.plot(v, func(v, plsq[0]), label=u"fitting curve")
    pl.legend()
    pl.savefig('fitting')
    pl.show()

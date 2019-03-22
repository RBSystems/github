#!/usr/bin/python2

#part of phonon, to find the proper delta_x
#pre_processing part: generate all input files and Pbs files for bw

import os
import sys
from math import *

if __name__ == "__main__":

    file_pbs = 'rmg.pbs'
    pre_pathname = 'supercell'
    flag = 1
    i = 1
    width =3
    while flag:
        pathname = '{pre_pathname}-{0:0{width}}'.format(i,
                                                 pre_pathname=pre_pathname,
                                                 width=width)
        if os.path.exists(pathname):
                i += 1
                os.chdir(pathname)
                os.system('qsub %s'% file_pbs)
                os.chdir('..')
        else:
            flag = 0

    print ('All jobs submitted!\n')
    print ('    total jobs: %d\n'%(i-1))

    #for i in range(n):
    #    f_new = open('%s.%d.pbs'%(prefix,i),'w')
    #    for j in range(n_lines):
    #        if "rmg" not in all_lines_old[j]:
    #            f_new.write(all_lines_old[j])
    #        else:
    #            f_new.write("%s.%d"%(all_lines_old[j][:-1],i))
    #    f_new.close()
    #    os.system("qsub '%s.%d.pbs'"%(prefix,i))

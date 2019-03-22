#!/usr/bin/python2

#replace words in many files

import os
import sys
from math import *

if __name__ == "__main__":


    words_old = "1.0e-08"
    words_new = "1.0e-07"

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
            f = open('%s/supercell.in'% pathname)
            lines_old = f.readlines()
            os.system('rm %s/supercell.in'% pathname)
            lines_new = '\n'
            for j in range(len(lines_old)):
                if words_old in lines_old[j]:
                    lines_new +=  lines_old[j].replace(words_old, words_new)
                else:
                    lines_new += lines_old[j]

            f = open('%s/supercell.in'% pathname, 'w')
            f.write(lines_new)
            f.close()
        else:
            flag = 0

    print ('Done!\n')
    print ('    total dirs: %d\n'%(i-1))
    #for i in range(n):
    #    f_new = open('%s.%d.pbs'%(prefix,i),'w')
    #    for j in range(n_lines):
    #        if "rmg" not in all_lines_old[j]:
    #            f_new.write(all_lines_old[j])
    #        else:
    #            f_new.write("%s.%d"%(all_lines_old[j][:-1],i))
    #    f_new.close()
    #    os.system("qsub '%s.%d.pbs'"%(prefix,i))

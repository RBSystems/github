#! /usr/bin/env python

'''
write pbs files for all subdirectories in format disp-***.
'''

import os
import sys
from math import *

if __name__ == "__main__":

    pwd = os.getcwd()
    all_dir = []
    for (dirpath, dirnames, filenames) in os.walk(pwd):
        dirnames.sort()
        all_dir.extend(dirnames)
        break

    file_pbs = 'lsf.sh'

    with open(file_pbs) as f:
        lines = f.readlines()

    #for i in range(len(lines)):
    #    if ('-J' in lines[i]) and ('BSUB' in lines[i]):
    #        pre_name = lines[i].split()[-1]
    #        line_marked = i

    for this_dir in all_dir:
        work_dir = os.path.join(pwd, this_dir)

        f = open('%s/%s'%(work_dir, file_pbs),'w')
        for i in range(len(lines)):
            #if i == line_marked:
            #    tmp = lines[i].split()
            #    description = this_dir
            #    #description = "".join('%s+%s'%(pre_name, this_dir))
            #    f.write('#BSUB -J %s\n'% description)
            if 'cd' in lines[i]:
                f.write('cd %s\n'% work_dir)
            else:
                f.write(lines[i])
        f.close()
        os.system('sed -i "s/null/%s/g" %s/%s'%(this_dir, work_dir, file_pbs))

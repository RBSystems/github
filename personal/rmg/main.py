#!/usr/bin/python2

# batch script for RMG by zjyx at NCSU.
# start with *xyz, *cif, et. al. file, end at dos/band/animation.
# Work sequences are as follow:
#   1. orig_data/: grab positions information
#   2. /unitcell: generate standard input file for rmg
#   3. relaxtion: relax structure.i.e, optimazation
#   4. supercell: generate all supercells with displacements, and quench electrons
#   5. results: calculate all possible results. like dos/phonon/animation. etc

import os
import sys

if __name__ == "__main__":

    file_input = 'supercell.in'
    pre_pathname = 'supercell'
    path_dst = 'zjyx@panther.chips.ncsu.edu:/home/zjyx/projects/rmg_test_ORNL/H2SO4/supercell/supercells/'
    flag = 1
    i = 1
    width =3

    print ('Destination path is: \n     %s\n\n'% path_dst)
    choice = raw_input('enter "y" to move on...\n')
    if choice.lower() != 'y':
        print ('SCP aborted!\n')
        sys.exit()

    while flag:
        pathname = '{pre_pathname}-{0:0{width}}'.format(i,
                                                 pre_pathname=pre_pathname,
                                                 width=width)
        if os.path.exists(pathname):
            i += 1 
            os.chdir(pathname)
            if os.system('scp %s.00.log %s%s'%(file_input, path_dst, pathname)):
                print ('Error when coping %s.00.log!\n'% file_input)
                sys.exit(1)
            os.chdir('..')
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

#!/usr/bin/python2

#part of phonon, to find the proper delta_x

import os
import sys
from math import *
from numpy import *

if __name__ == "__main__":

    jobs = []
    jobs_id = []
    jobs_postfix = []

    os.system("qstat -u zhang7 > qdel.tmp")
    
    with open('qdel.tmp') as f:
        lines = f.readlines()

    for line in lines:
        if 'zhang7' in line:  
            jobs.append(line.split()[0])

    for i in range(len(jobs)):
        jobs_tmp = jobs[i].split('.')
        jobs_id.append(int(jobs_tmp[0]))
        jobs_postfix.append(jobs_tmp[1])

    print ('Total jobs: %d\n'%(len(jobs)))
    print ('Jobs ID:\n')
    for i in range(len(jobs)):
        print ('    %10d....deleted\n')%(jobs_id[i])
        os.system('qdel %d'%(jobs_id[i]))

    os.system('rm qdel.tmp')
    exit()
    for i in range(end-start+1):
        job_curr = start + i
        os.system('qdel %d.%s'%(job_curr,node))

#    3191717.nid11293

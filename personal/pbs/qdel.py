#!/usr/bin/python2

# qdel all jobs (if job_begin and job_end defined,
# then qdel all jobs between them)

import os
import sys
from math import *
from numpy import *

if __name__ == "__main__":

    job_begin = None
    job_end = None
    flag = None
    jobs = []
    jobs_id = []
    jobs_postfix = []

    os.system("qstat -u z8j > qdel.tmp")
    
    with open('qdel.tmp') as f:
        lines = f.readlines()

    for line in lines:
        if 'z8j' in line:  
            jobs.append(line.split()[0])

    for i in range(len(jobs)):
        jobs_tmp = jobs[i].split('.')
        jobs_id.append(int(jobs_tmp[0]))
        jobs_postfix.append(jobs_tmp[1])

    print ('Total number of jobs: %d\n'%(len(jobs)))

    print ('Jobs ID:\n')

    if not job_begin and not job_end:
        flag = 0
        print ('No begin nor end job defined, deleting all jobs...\n')
        for i in range(len(jobs)):
            print ('    %10d....deleted\n')%(jobs_id[i])
            os.system('qdel %d'%(jobs_id[i]))
    elif not job_begin and job_end:
        flag = 1
        print ('No begin job defined, deleting selected jobs...\n')
        for i_job in range(jobs_id[0], job_end):
            print ('    %10d....deleted\n')%(i_job+1)
            os.system('qdel %d'%(i_job+1))
    elif job_begin and not job_end:
        flag = 2
        print ('No end job defined, deleting selected jobs...\n')
        for i_job in range(job_begin, jobs_id[-1]):
            print ('    %10d....deleted\n')%(i_job+1)
            os.system('qdel %d'%(i_job+1))
    elif job_begin and job_end:
        flag = 3
        print ('Begin and end job defined, deleting selected jobs...\n')
        for i_job in range(job_begin, job_end):
            print ('    %10d....deleted\n')%(i_job+1)
            os.system('qdel %d'%(i_job+1))
    else:
        print ('Something wrong...\n')
        sys.exit(1)

    os.system('rm qdel.tmp')
    exit()


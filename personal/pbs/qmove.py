#!/usr/bin/python2

# qdel all jobs (if job_begin and job_end defined,
# then qdel all jobs between them)

import os
import sys
from math import *
from numpy import *

if __name__ == "__main__":

    job_begin = 6293780
    job_end = 6293900

    for i in range(job_begin, job_end):
        os.system('qmove normal %d'% i)

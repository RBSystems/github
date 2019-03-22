#! /usr/bin/env python

"""
    add header before every supercell input file
"""

import os
import sys

def path(i):
    return 'supercells/supercell-%03d'%i

i = 0
while os.path.isdir(path(i)):
    print path(i)
    os.system('cat header %s/supercell.in > %s/tmp.in'%(path(i), path(i)))
    os.system('mv %s/tmp.in %s/supercell.in'%(path(i), path(i)))
    i += 1
print i

import os
import sys

file_pos = sys.arg[1]
try:
    os.system('cif2cell --no-reduce %s'% file_pos)
except:
    print ('Cif2cell need to be installed!\n')
    sys.exit(1)

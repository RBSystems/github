#! /usr/bin/env python

# calculate force costant matrix

import os
import sys

i = 1
width = 3

if os.path.isfile('qe.in'):
    mode = 'pwscf'
    log_filename = 'supercell.00.out'
    pre_pathname = "supercell"
    supercell_dir = "supercells"
elif os.path.isfile('unitcell.in'):
    mode = 'rmg'
    log_filename = 'supercell.in.00.log'
    pre_pathname = "supercell"
    supercell_dir = "supercells"
elif os.path.isfile('SPOSCAR'):
    mode  = 'vasp'
    log_filename = 'vasprun.xml'
    pre_pathname = "disp"
    supercell_dir = "disps"
else:
    print "Error: unitcell not found, exit."
    sys.exit(1)

force_cmd = 'python /home/zjyx/softwares/phonopy-1.10.10/bin/phonopy --%s -f'% mode

while True:
    path_tmp = '{pre_pathname}-{0:0{width}}'.format(i,
                                             pre_pathname=pre_pathname,
                                             width=width)
    pathname = supercell_dir + ('/%s'% path_tmp)
    if os.path.exists(pathname):
            i += 1
            force_cmd += ' %s/%s'%(pathname, log_filename)
    else:
        break

os.system('%s'% force_cmd)
#try:
#    os.system('%s'% force_cmd)
#except:
#    print "Error: cannot operate command, exit."
#    sys.exit(1)
#else:
#    print ('Force sets done!\n')
#    print ('    total files: %d\n'%(i-1))

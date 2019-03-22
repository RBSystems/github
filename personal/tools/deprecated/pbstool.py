#!/usr/bin/env python

'''
Program: generate and submit pbs files for RMG
         save rmg.in/supercell.in for later debug
    zjyx, @2017/02, ORNL

ChangeLogs:
    1. remove queue tags, which will be determined by walltime and host
        automatically.

TODO:
    define a class for pbs file
'''

import os
import sys

def get_user():
    import getpass
    return getpass.getuser()

def get_host():
    import socket
    hostname = socket.gethostname()
    if 'or-condo' in hostname:
        return 'Cades'
    elif 'h2o' in hostname:
        return 'BlueWaters'
    elif 'titan' in hostname:
        return 'Titan'
    else:
        print 'Unknow host, exit.\n'
        sys.exit(1)

##################################################
#   some environment variables
##################################################

pwd         = os.getcwd()
user        = get_user()
home_path   = os.path.expanduser('~')
host        = get_host()


##################################################
#   user setting parameters
##################################################

nodes       = 8
time        = [0, 20] # in units of hours, mins
name        = 'debug'+'@'+pwd
exe_input   = 'rmg.in'
threads     = 1

# noramally following lines need no modification
queue       = None
is_submit   = True
exe_path    = home_path+'/bin/rmg-cpu'

##################################################
#   Do not modify following lines
##################################################

#class pbs:
#    def __init__(self,
#                 system='virtues',
#                 nodes=1,
#                 time='00:30:00',
#                 name='test',
#                 queue='batch',
#                 threads=1):
#        self._set_methods = {'system': self._set_system,
#                             'nodes':  self._set_nodes,
#                             'time':   self._set_time,
#                             'name':   self._set_name,
#                             'queue':  self._set_queue,
#                             'threads':self._set_threads}
#        self._tags = {'system': None,
#                      'nodes':  None,
#                      'time':   None,
#                      'name':   None,
#                      'queue':  None,
#                      'threads':None}
#        self._set_all()
#
#    def _set_all(self):
#        pass
#
#    def get_tags(self):
#        return self._tags



# check if those varibles make sense
##def check_params():
##    if 32%(threads)!=0:
##        print "OMP_NUM_THREADS error, exit.\n"
##        sys.exit(1)
##
##def build_pbs():
##    pass
##
##def write_pbs():
##    pass

# check parameters setting
print '\n'
if 32%(threads):
    print "OMP_NUM_THREADS error, exit.\n"
    sys.exit(1)

if not os.path.isfile(exe_input):
    print "RMG input file(%s) not found, exit.\n"% exe_input
    sys.exit(1)

if host == 'BlueWaters':
    all_queues = ['debug', 'normal', 'high']
    if queue and queue not in all_queues:
        print 'Queue error, exit.\n'
        sys.exit(1)
    # ignore if queue is high
    if queue != 'high':
        if time[0]*60+time[1] <= 30:
            queue = all_queues[0]
            print "Walltime <= 30 mins, queue will be %s.\n"% queue
        else:
            queue = all_queues[1]
            print "Walltime > 30 mins, queue will be %s.\n"% queue
    #if queue == 'normal' and (time[0]*60+time[1]<30):
    #    print "Walltime is smaller than 30 mins, resetting 'queue' to 'debug'3.\n"
    #    queue = 'debug'
    #if queue == 'debug' and (time[0]*60+time[1]>30):
    #    print 'Walltime for debug error, resetting to 30 mins.\n'
    #    time = [0, 30]
elif host == 'Cades':
    all_queues = ['batch', 'long']
    if queue and queue not in all_queues:
        print 'Queue error, exit.\n'
        sys.exit(1)
    if time[0] > 48:
        queue = all_queues[1]
        print "Walltime > 48 hrs, queue will be %s.\n"% queue
    else:
        queue = all_queues[0]
        print "Walltime <= 48 hrs, queue will be %s.\n"% queue

# PBS file

ppn_use     = divmod(32, threads)[0]
cores       = int(nodes*32/threads)
time_pbs    = "%02d:%02d:00"%(time[0], time[1])

pbs_dict = {'queue':        queue,
            'time':         time_pbs,
            'nodes':        nodes,
            'name':         name,
            'threads':      threads,
            'pwd':          pwd,
            'cores':        cores,
            'exe_path':     exe_path,
            'exe_input':    exe_input,
            'ppn_use':      ppn_use}

lines_bw = '''#!/bin/bash

#PBS -A baec
#PBS -q %(queue)s
#PBS -m ea
#PBS -M zjyx1991@foxmail.com
#PBS -j oe
#PBS -l walltime=%(time)s
#PBS -l nodes=%(nodes)d:ppn=32:xe
#PBS -N %(name)s

source /opt/modules/default/init/bash
module swap PrgEnv-cray PrgEnv-gnu
module list

export OMP_NUM_THREADS=%(threads)d

export MPICH_MAX_THREAD_SAFETY=serialized
export OMP_WAIT_POLICY=passive
export MPICH_ENV_DISPLAY=1
export MPICH_ALLREDUCE_NO_SMP=1
ulimit -a
export CRAY_CUDA_PROXY=1
export MPICH_UNEX_BUFFER_SIZE=362914560
export MPICH_MAX_SHORT_MSG_SIZE=3200

cd %(pwd)s

date

aprun -n %(cores)d -N %(ppn_use)d -d %(threads)d -cc numa_node %(exe_path)s %(exe_input)s

date
'''%(pbs_dict)

lines_cades = '''#!/bin/bash

#PBS -A sns
#PBS -q batch
#PBS -m ea
#PBS -M zjyx1991@foxmail.com
#PBS -j oe
#PBS -l qos=condo
#PBS -W group_list=cades-virtues
#PBS -l walltime=%(time)s
#PBS -l nodes=%(nodes)d:ppn=32
#PBS -N %(name)s

module load PE-gnu
module list

export OMP_NUM_THREADS=%(threads)d

cd %(pwd)s

date

mpirun -np %(cores)d --bind-to none --map-by ppr:%(ppn_use)d:node:pe=%(threads)d %(exe_path)s %(exe_input)s

date
'''%(pbs_dict)

# write PBS
with open('pbs.rmg', 'wb') as f:
    if host == 'Cades':
        f.write(lines_cades)
    elif host == 'BlueWaters':
        f.write(lines_bw)

# submit pbs
if is_submit:
    print "Submitting jobs...\n"
    os.system('qsub pbs.rmg')


with open('pbs.rmg', 'rb') as f:
    lines_pbs = f.readlines()

with open('%s'% exe_input, 'rb') as f:
    lines_in = f.readlines()

lines_conf = ''
lines_conf += '#! /bin/bash'+'\n\n'
lines_conf += 'Computer name: %s'%host + '\n\n'
lines_conf += '*'*80+'\n'
lines_conf += '*'+' '*30+'PBS LINES: %6d'%len(lines_pbs)+' '*31+'*\n'
lines_conf += '*'*80+'\n\n'
lines_conf += '-'*80+'\n'
lines_conf += ''.join(lines_pbs)
lines_conf += '-'*80+'\n\n'
lines_conf += '*'*80+'\n'
lines_conf += '*'+' '*29+'INPUT LINES: %6d'%(len(lines_in))+' '*30+'*\n'
lines_conf += '*'*80+'\n\n'
lines_conf += '-'*80+'\n'
lines_conf += ''.join(lines_in)
lines_conf += '-'*80+'\n\n'

# save configurations: including input file and pbs file
i = 0
while os.path.isfile('runconf.%02d'%(i)):
    i += 1

with open('runconf.%02d'% i, 'wb') as f:
    f.write(lines_conf)

# old version
#os.system("echo '#! /bin/bash\n' >> runconf.%02d "% i)
#os.system("echo '***************************************' >> runconf.%02d "% i)
#os.system("echo '*               PBS FILE              *' >> runconf.%02d "% i)
#os.system("echo '***************************************' >> runconf.%02d "% i)
#os.system("echo '\n---------------------------------------\n' >> runconf.%02d "% i)
#os.system('cat >> runconf.%02d < pbs.rmg'%(i))
#os.system("echo '\n---------------------------------------\n' >> runconf.%02d "% i)
#os.system("echo '***************************************' >> runconf.%02d "% i)
#os.system("echo '*             INPUT FILE              *' >> runconf.%02d "% i)
#os.system("echo '***************************************\n' >> runconf.%02d "% i)
#os.system("echo '\n---------------------------------------\n' >> runconf.%02d "% i)
#os.system('cat >> runconf.%02d < %s'%(i, exe_input))
#os.system("echo '\n---------------------------------------\n' >> runconf.%02d "% i)
#os.system('cp %s %s.%02d'%(exe_input, exe_input, i))
#os.system('cp pbs.rmg pbs.rmg.%02d'%(i))

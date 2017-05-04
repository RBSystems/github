#! /usr/bin/env python

# Program: submit pbs jobs for virtues under limitation of procs etc

import os
import sys
import time

# get total number of current active procs
def get_runque_procs():

    procs_tmp = 0
    time_format='%Y%m%d%H%M%S'
    time_tmp = time.strftime(time_format, time.localtime())
    file_tmp = 'tmp.qi.%s'% time_tmp

    os.system("qstat -u z8j > %s"%(file_tmp))

    with open('%s'% file_tmp) as f:
        lines = f.readlines()

    for line in lines:
        if ('z8j' in line) and (line.split()[-2] == 'R' or line.split()[-2] == 'Q'):
            procs_tmp += int(line.split()[6])

    os.system('rm %s'%(file_tmp))

    return procs_tmp

# read procs to be requested
def get_req_procs():

    with open(file_pbs) as f:
        lines = f.readlines()

    for line in lines:
        if 'nodes' in line and 'ppn' in line:
            key_words = line.split()[-1]
            break

    nodes = int(key_words.split(':')[0].split('=')[-1])
    ppn = int(key_words.split('=')[-1])

    req_procs = nodes*ppn

    return req_procs

# check if the pbs file has already been submitted
def check_job_existed(job_to_sub):

    if job_to_sub not in running_jobs:
        return True
    else:
        return False

def get_pathname(i):

    pathname = '{pre_pathname}-{0:0{width}}'.format(i,
                                             pre_pathname=pre_pathname,
                                             width=width)
    return pathname

class PbsIn():
    def __init__(self, lines):
        self._set_methods = {'walltime': self._set_walltime,
                             'queue': self._set_queue,
                             'nodes': self._set_nodes,
                             'procs': self._set_procs,
                             'jobname': self._set_jobname}
        self._tags = {'walltime': None,
                      'queue': None,
                      'nodes': None,
                      'procs': None,
                      'jobname': None}

        self._collect(lines)

    def get_tags(self):
        return self._tags

    def _collect(self, lines):
        elements = []
        tag = None
        for line_tmp in lines:
            if 'PBS' in line_tmp:
                line = line_tmp.split('#')[1]
            else:
                line = line_tmp.split('#')[0]

            if len(line) < 2:
                continue

            if 'PBS' in line:
                if ('-l' in line) and ('walltime' in line):
                    line_replaced = line.replace('=', ' ').replace(':', ' ')
                    words = line_replaced.lower().split()
                elif ('-l' in line) and ('nodes' in line):
                    line_replaced = line.replace('=', ' ').replace(':', ' ')
                    words = line_replaced.lower().split()
                elif '-q' in line:
                    words = line.lower().split()
                elif '-N' in line:
                    words = line.lower().split()

            for val in words:
                if val.lower() in self._set_methods:
                    tag = val.lower()
                    elements[tag] = []
                elif tag is not None:
                    elements[tag].append(val)

        for tag in ['walltime', 'resources', 'name']:
            if tag not in elements:
                print ('%s is not found in the pbs file.'% tag)
                sys.exit(1)

        for tag, self._values in elements.iteritems():
            self._set_methods[tag]()

    def _set_walltime(self):
        walltime = [int(self._values[0]),
                    int(self._values[1]),
                    int(self._values[1])]
        self._tag['walltime'] = walltime

    def _set_resources(self):
        resources = [int(self._values[0]),
                     int(self._values[1])]
        self._tag['resources'] = resources

    def _set_queue(self):
        queue = self._values[0]
        self._tag['queue'] = queue

    def _set_jobname(self):
        jobname = self._values[0]
        self._tag['jobname'] = jobname

if __name__ == "__main__":

#####################################################################
#   variables may be defined accordingly

    # sample pbs file
    file_pbs = 'pbs.sh'
    # log file name
    file_log = 'log.pbs'
    # common name of all subdirectories
    pre_pathname = 'supercell'
    # width of directories' name
    width = 3
    # max number of proc that will be used
    max_procs = 512
    # sleep time if max procs has been used
    sleep_time = 100
    # set default time format
    time_format='%Y-%m-%d %X'

#   end of variables
#####################################################################

    i = 11

    pwd = os.getcwd()

    pathname = get_pathname(i)
    while os.path.exists(pathname):

        os.chdir(pathname)

        runque_procs = get_runque_procs()
        req_procs = get_req_procs()
        # need to decide which way is better
        while ( runque_procs + req_procs ) > max_procs:
        #while run_procs > max_procs:
            time_tmp = time.strftime(time_format, time.localtime())
            sleep_info = ('%s@%s: Running/queued procs [%5d], new requested'
                          ' procs [%5d]. Sleeping for [%4d] secs...'
                            %(pathname, time_tmp, runque_procs, req_procs, sleep_time))
            print sleep_info
            os.system("echo %s >> %s"%(sleep_info, file_log))
            time.sleep(sleep_time)

            runque_procs = get_runque_procs()
            #req_procs = get_req_procs()

        if not os.path.exists('./supercell.in.00.rmsdv.xmgr'):
            os.system('rm supercell.in.*')
            os.system('qsub %s'% file_pbs)
            sub_info = ('Job for %s is submitted.'% pathname)
            os.system("echo %s >> %s"%(sub_info, file_log))
            # submitted jobs info delay
            time.sleep(30)

        i += 1
        pathname = get_pathname(i)
        os.chdir('..')

    print ('\n\n\n All jobs submitted!\n')
    print ('    total jobs: %d\n'%(i-1))

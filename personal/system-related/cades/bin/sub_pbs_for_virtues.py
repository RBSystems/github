#!/usr/bin/python2

# pre_process part: sub pbs files in a limit that total running
# processors' number is smaller than max_procs

import os
import sys
import time

# get total number of current active procs
def get_run_procs():

    procs_tmp = 0
    time_format='%Y%m%d%H%M%S'
    time_tmp = time.strftime(time_format, time.localtime())
    file_tmp = 'tmp.qi.%s'% time_tmp

    os.system("qstat -u z8j > %s"%(file_tmp))

    with open('%s'% file_tmp) as f:
        lines = f.readlines()

    for line in lines:
        if ('z8j' in line) and (line.split()[-2] == 'R'):
            procs_tmp += int(line.split()[6])

    os.system('rm %s'%(file_tmp))

    return procs_tmp

# get queue procs
def get_que_procs():
    return

# read procs to be requested
def get_req_procs():

    with open('rmg.pbs') as f:
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
    file_pbs = 'rmg.pbs'
    # log file name
    log_name = 'log.pbs'
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

    i = 1

    pwd = os.getcwd()
    f = open(log_name, 'wr')

    pathname = get_pathname(i)
    while os.path.exists(pathname):

        run_procs = get_run_procs()
        que_procs = get_que_procs()
        req_procs = get_req_procs()
        # need to decide which way is better
        while ( run_procs + que_procs + req_procs ) > max_procs:
        #while run_procs > max_procs:
            time_tmp = time.strftime(time_format, time.localtime())
            sleep_info = ('At %25s:\nRunning procs: [%5d], new requested'
                          ' procs: [%5d]. Will sleep for [%4d] secs...\n\n'
                            %(time_tmp, run_procs, req_procs, sleep_time))
            print sleep_info
            f.write(sleep_info)
            time.sleep(sleep_time)
            run_procs = get_run_procs()
            que_procs = get_que_procs()
            req_procs = get_req_procs()

        if (not os.path.exists('./supercell.in.00.rmsdv.xmgr') and
            not check_job_existed(job_to_sub)):
            os.chdir(pathname)
            os.system('rm supercell.in.*')
            os.system('qsub %s'% file_pbs)
            sub_info = 'Job %s is submitted.\n\n'% pathname
            f.write('%s'% sub_info)
            os.chdir('..')
            # avoid info updated not in time
            time.sleep(30)

        i += 1
        pathname = get_pathname(i)

    f.close()
    print ('\n\n\n All jobs submitted!\n')
    print ('    total jobs: %d\n'%(i-1))

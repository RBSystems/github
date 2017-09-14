#! /usr/bin/env python

'''
    Program: submit pbs jobs for virtues under limitation of procs etc

    TODO:
        1. add regular expression option for excluded dirs
'''

import os
import sys
import time

# read conf file
def read_conf(conf_file):
    with open(conf_file, 'rb') as f:
        conf_lines = f.readlines()
    for line in conf_lines:
        line = line.split('#')[0]
        if "exclude" in line.lower():
            values = line.split('=')[-1].split()
            pbs_conf['exclude'] = values
        elif "max_nodes" in line.lower():
            values = line.split('=')[-1]
            pbs_conf['max_nodes'] = int(values)
        elif "max_jobs" in line.lower():
            values = line.split('=')[-1]
            pbs_conf['max_jobs'] = int(values)
        elif "sleep" in line.lower():
            values = line.split('=')[-1]
            pbs_conf['sleep'] = float(values)
        elif "file_pbs" in line.lower():
            values = line.split('=')[-1]
            pbs_conf['file_pbs'] = str(values)
        elif "user_id" in line.lower():
            values = line.split('=')[-1].split()[0]
            pbs_conf['user_id'] = str(values)

# get total number of current active procs
def get_queued_nodes():

    nodes_tmp = 0
    time_format='%Y%m%d%H%M%S'
    time_tmp = time.strftime(time_format, time.localtime())
    file_tmp = 'tmp.qi.%s'% time_tmp

    os.system("qstat -u z8j > %s"%(file_tmp))

    with open('%s'% file_tmp) as f:
        lines = f.readlines()

    for line in lines:
        if ('z8j' in line) and (line.split()[-2] == 'Q'):
            nodes_tmp += int(line.split()[5])

    os.system('rm %s'%(file_tmp))

    return nodes_tmp

# get total number of current active procs
def get_running_nodes():

    nodes_tmp = 0
    time_format='%Y%m%d%H%M%S'
    time_tmp = time.strftime(time_format, time.localtime())
    file_tmp = 'tmp.qi.%s'% time_tmp

    os.system("qstat -u z8j > %s"%(file_tmp))

    with open('%s'% file_tmp) as f:
        lines = f.readlines()

    for line in lines:
        if ('z8j' in line) and (line.split()[-2] == 'R'):
            nodes_tmp += int(line.split()[5])

    os.system('rm %s'%(file_tmp))

    return nodes_tmp

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

    pbs_conf = {"file_pbs": "pbs.sh",
                "exclude": None,
                "name_log": "log.pbs",
                "max_nodes": 1e10,
                "ignore_if_existed": None,
                "sleep": 0
                }

    # read control file
    if len(sys.argv) > 1:
        pbs_conf_file = sys.argv[-1]
    else:
        pbs_conf_file = "qsub.conf"
    read_conf(pbs_conf_file)

    # set default time format
    time_format='%Y-%m-%d %X'
    submitted_job_counter = 0

    pwd = os.getcwd()
    file_log = os.path.join(pwd, pbs_conf['name_log'])

    all_dir = []
    for (dirpath, dirnames, filenames) in os.walk(pwd):
        all_dir.extend(dirnames)

    for this_dir in all_dir:
        if this_dir in pbs_conf['exclude']:
            continue

        work_dir = os.path.join(pwd, this_dir)
        os.chdir(work_dir)

        if pbs_conf['max_nodes'] == 0:
            os.system('qsub %s'%( pbs_conf['file_pbs']))
        else:
            queued_nodes = get_queued_nodes()
            running_nodes = get_running_nodes()
            while (queued_nodes + running_nodes) > pbs_conf['max_nodes']:
                time_tmp = time.strftime(time_format, time.localtime())
                sleep_msg = ('%s@%s: Running + queued nodes:%5d. Sleeping for [%4d] secs...'
                            %(time_tmp, this_dir, queued_nodes+running_nodes, pbs_conf['sleep']))
                print sleep_msg
                os.system("echo %s >> %s"%(sleep_msg, file_log))
                time.sleep(pbs_conf['sleep'])

                queued_noeds = get_queued_nodes()
                running_nodes = get_running_nodes()

            if not pbs_conf['ignore_if_existed'] or ( not os.path.exists(pbs_conf['ignore_if_existed'])):
                #if os.path.exists('./supercell.in.*'):
                #    os.system('rm supercell.in.*')
                os.system('qsub %s'% pbs_conf['file_pbs'])
                sub_msg = ('Job for %s is submitted.'% this_dir)
                os.system("echo %s >> %s"%(sub_msg, file_log))
                # submitted jobs info delay
                time.sleep(30)

        submitted_job_counter += 1

    print ('\n\n\n All jobs submitted: %d\n'% submitted_job_counter)
    os.system("echo %s >> %s"%('Done!', file_log))

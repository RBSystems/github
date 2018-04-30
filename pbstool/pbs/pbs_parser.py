import os
import sys
import datetime
from pbs_opts import *

# add set and get functions here, cause it may be modified
class ConfParser:
    def __init__(self, filename=None):
        self._confs = { 'nodes':    param_prop['nodes']['default'],
                        'time':     param_prop['time']['default'],
                        'exeinput': param_prop['exeinput']['default'],
                        'exepath':  param_prop['exepath']['default'],
                        'account':  param_prop['account']['default'],
                        'module':   param_prop['module']['default']
        }
                        #'force_sub':  param_prop['force_sub']['default'],
                        #'depend':  param_prop['depend']['default'],

        self._params = {}
        self._workdir=""

        if filename is not None:
            self.read_file(filename)

        self.parse_conf()

    def setting_error(self, msg):
        print(msg)
        print("Please check the setting tags.")
        sys.exit(1)

    def read_file(self, filename):
        confs = self._confs
        with open(filename, 'rb') as f:
            lines_conf = f.readlines()
        for line in lines_conf:
            line_tmp = line.split('#')[0]
            if line_tmp == '':
                continue
            if line_tmp.find('=') != -1:
                left, right = [x.strip() for x in line_tmp.split('=')]
                left = left.lower()
                if left != "module":
                    confs[left] = right
                else:
                    confs[left].append(right)

    def parse_conf(self):
        confs = self._confs

        for conf_key in confs.keys():
            if conf_key == 'exepath':
                self.set_param('exepath', confs['exepath'])
                break

        for conf_key in confs.keys():
            if conf_key == 'nodes':
                self.set_param('nodes', confs['nodes'])
            elif conf_key == 'time':
                self.set_param('time', confs['time'])
            elif conf_key == 'exeinput':
                self.set_param('exeinput', confs['exeinput'])
            elif conf_key == 'exepath': # avoid unrecognized tag error
                pass
            #    self.set_param('exepath', conf['exepath'])
            elif conf_key == 'threads':
                self.set_param('threads', confs['threads'])
            elif conf_key == 'name':
                self.set_param('name', confs['name'])
            elif conf_key == 'is_submit':
                self.set_param('is_submit', confs['is_submit'])
            elif conf_key == 'queue':
                self.set_param('queue', confs['queue'])
            elif conf_key == 'exeoutput':
                self.set_param('exeoutput', confs['exeoutput'])
            elif conf_key == 'force_sub':
                self.set_param('force_sub', confs['force_sub'])
            elif conf_key == 'depend':
                self.set_param('depend', confs['depend'])
            elif conf_key == 'account':
                self.set_param('account', confs['account'])
            elif conf_key == 'module':
                self.set_param('module', confs['module'])
            else:
                print("Warning! Unrecoginized settings: %s"% conf_key)

    def set_param(self, key, val):
        _param = param_prop[key]
        # TODO: need to detect if a default value has been modified intendly
        if _param['required'] and val == _param['default']:
            msg = "Error: required tags %s not found."% key.upper()
            self.setting_error(msg)
        #consider canceling this part, check mandatory part one by one manually TODO
        if key == 'cores':
            self._set_cores(val)
        elif key == 'name':
            self._set_name(val)
        elif key == 'is_submit':
            self._set_is_submit(val)
        elif key == 'nodes':
            self._set_nodes(val)
        elif key == 'time':
            self._set_time(val) 
        elif key == 'exeinput':
            self._set_exeinput(val) 
        elif key == 'exepath':
            self._set_exepath(val) 
        elif key == 'exeoutput':
            self._set_exeoutput(val) 
        elif key == 'threads':
            self._set_threads(val) 
        elif key == 'queue':
            self._set_queue(val) 
        elif key == 'module':
            self._set_module(val) 
        elif key == 'account':
            self._set_account(val) 
        elif key == 'force_sub':
            self._set_force_sub(val) 
        elif key == 'depend':
            self._set_depend(val) 
            #self._set_account(val) 
        else:
            msg = "Error: %s type tag could not be identified."% key.upper()
            self.setting_error(msg)

#    def _set_nodes(self, val):
#        self._params['nodes'] = int(val)
#
#    def _set_time(self, val):
#        self._params['time'] = [int(ele) for ele in val.split()]
#
#    def _set_exeinput(self, val):
#        self._params['exeinput'] = val
#
#    def _set_exeoutput(self, val):
#        self._params['exeoutput'] = str(val)
#
#    def _set_exepath(self, val):
#            pass
#            #self._set_account(val) 
#        else:
#            msg = "Error: %s type tag could not be identified."% key.upper()
#            self.setting_error(msg)

    def _set_nodes(self, val):
        self._params['nodes'] = int(val)

    def _set_time(self, val):
        self._params['time'] = [int(ele) for ele in val.split()]

    def _set_depend(self, val):
        if type(val) == list:
            self._params['depend'] = val
        else:
            dep_crit = val.split(':')[0]
            dep_jobs = val.split(':')[1].split(',')
            depend = [dep_crit, [int(ele) for ele in dep_jobs]]
            self._params['depend'] = depend

    def _set_exeinput(self, val):
        self._params['exeinput'] = val

    def _set_force_sub(self, val):
        if type(val) == bool:
            self._params['force_sub'] = val
        elif val.lower() in ['false', 'f']:
            self._params['force_sub'] = False
        elif val.lower() in ['true', 't']:
            self._params['force_sub'] = True
        else:
            msg = "Error: Unknown value for tag FORCE_SUB, exit."
            self.setting_error(msg)

    def _set_exeoutput(self, val):
        self._params['exeoutput'] = str(val)

    def _set_exepath(self, val):
        self._params['exepath'] = str(val)
        if 'vasp' in self._params['exepath'].lower():
            #print "hhah"
            vasp_in = ['INCAR', 'POSCAR', 'POTCAR', 'KPOINTS']
            #self.set_param('exeinput', vasp_in)
            self._confs['exeinput'] = vasp_in

    def _set_module(self, val):
        self._params['module'] = val

    def _set_account(self, val):
        self._params['account'] = val

    def _set_threads(self, val):
        self._params['threads'] = int(val)

    def _set_name(self, val):
        self._params['name'] = str(val)

    def _set_is_submit(self, val):
        if val.lower() in ['false', 'f']:
            self._params['is_submit'] = False
        elif val.lower() in ['true', 't']:
            self._params['is_submit'] = True
        else:
            msg = "Error: Unknown value for tag IS_SUBMIT, exit."
            self.setting_error(msg)

    def _set_queue(self, val):
        self._params['queue'] = str(val).lower()

    #def _set_cores(self, val=None):
    #    if val:
    #        self._params['cores'] = val
    #    else:
    #        self._params['cores'] = 32*self._params['nodes']/self._params['threads']
    def _set_cores(self, val):
        self._params['cores'] = val

    def validate_params(self):
        pass

    def validate_name(self, parent_wd, post_wd):
        name = self._params['name']
        self._params['name'] = (name+'@'+parent_wd+'/'+post_wd).rstrip('/')

    def validate_is_submit(self):
        is_submit = self._params['is_submit']
        exename = self._params['exename']
        if not is_submit:
            print "%s: Debug mode, job will not be submitted.\n"% exename.upper()
        
    def validate_threads(self, host):
        threads  = self._params['threads']
        if host.lower() == "titan":
            ppn = 16
        else:
            ppn = 32
        if ppn%(threads):
            msg = "Error: OMP_NUM_THREADS is not set correctly, exit."
            self.setting_error(msg)

    def validate_account(self, host):
        account = self._params['account']
        if host.lower() == 'titan':
            all_accounts = ['nti108', 'mat049']
        elif host.lower() == "cades":
            all_accounts = ["sns"]
        elif host.lower() == "bluewaters":
            all_accounts = ["baec"]

        if account not in all_accounts:
            msg = "Error: ACCOUNT value not in the list, exit."
            self.setting_error(msg)

    def validate_cores(self, host):
        nodes =  self._params['nodes']
        cores =  self._params['cores']
        threads =  self._params['threads']
        if host.lower() == "titan":
            ppn = 16
        else:
            ppn = 32

        if not cores:
            self._set_cores(ppn*nodes/threads)
        else:
            if cores > ppn*nodes/threads:
                msg =  "Error: Cores exceeds maximum limit set by nodes/threads, exit."
                self.setting_error(msg)

    def validate_exepath(self):
        # skip if force submit
        #if self._params['force_sub']:
        #    return
        rmg_exe_list = ['rmg-cpu', 'rmg-cpu-MulKpt']
        qe_exe_list = ['pw.x', 'ph.x', 'q2r.x', 'matdyn.x', 'lambda.x', 'epw.x', 'd3q.x', 'd3_q2r.x', 'd3_qq2rr.x', 'd3_asr3.x', 'd3_sparse.x', 'd3_lw.x', 'd3_tk.x']
        vasp_exe_list = ['vasp_std', 'vasp_ncl', 'vasp_gam']
        castep_exe_list = ['castep.mpi']
        exepath  = self._params['exepath']
        exename  = os.path.basename(exepath)
        if not os.path.isfile(exepath):
            msg = "Error: Executable %s does not exist, exit."% exepath
            self.setting_error(msg)
        if exename in rmg_exe_list:
            self._params['exename'] = 'RMG'
            #print "EXE name: %s"% 'RMG'
        elif exename in qe_exe_list:
            self._params['exename'] = 'QE'
            #print "EXE name: %s"% 'QE'
        elif exename in vasp_exe_list:
            self._params['exename'] = 'VASP'
        elif exename in castep_exe_list:
            self._params['exename'] = 'CASTEP'
        elif self._params['force_sub']:
            self._params['exename'] = 'others'
        else:
            msg = "Error: unknown exe, exit."
            self.setting_error(msg)
            #print "EXE name: %s"% 'VASP'

    def validate_module(self):
        from subprocess import Popen, PIPE
        p = Popen(['module avail'], stdout=PIPE, stderr=PIPE, shell=True)
        _out, _err = p.communicate()
        _outerr = _out + _err

        modules = self._params['module']
        #print modules
        #all_mods = subprocess.call()
        # cades module avail will be printed to stderr, thus you cannot get stdout
        #all_mods = os.popen('module avail').read()
        for _module in modules:
            if (not os.path.isfile(_module)) and ("%s"% _module not in _outerr):
                print "Warning: module %s does not exist."% _module

    def validate_exeinput(self):
        exeinput = self._params['exeinput']
        exename = self._params['exename']
        if exename == 'VASP':
            for _vasp_in in exeinput:
                if not os.path.isfile(_vasp_in):
                    msg = "Error: %s input file %s not found, exit."%(exename, _vasp_in)
                    self.setting_error(msg)
        elif exename == 'CASTEP':
            for _castep_in in [exeinput+'.cell', exeinput+'.param']:
                if not os.path.isfile(_castep_in):
                    msg = "Error: %s input file %s not found, exit."%(exename, _castep_in)
                    self.setting_error(msg)
        elif not os.path.isfile(exeinput):
            msg = "Error: %s input file %s not found, exit."%(exename, exeinput)
            self.setting_error(msg)

        self.check_exeinput(exename, exeinput)

    # check if input arguments make sense
    def check_exeinput(self, exename, exeinput):
        if exename == "RMG":
            from interface import rmg
            in_args = rmg.RmgIn(exeinput)
            rmg.validate_rmgin(in_args)
        elif exename == "CASTEP":
            from interface import castep
            cell_args = castep.CellIn(exeinput+'.cell')
            param_args = castep.ParamIn(exeinput+'.param')
            castep.validate_cell(cell_args)
            castep.validate_param(param_args)
        #elif exename == 'qe':
        #    in_args = QeIn(exeinput)

    def validate_exeoutput(self):
        exeoutput = self._params['exeoutput']
        if self._params['exename'] == 'VASP':
            pass
        elif exeoutput.lower() == 'none':
            exeoutput_pre = self._params['exeinput'].split('.in')[0]
            i = 0
            #while os.path.isfile("%sy%02d"%(exeoutput_pre, i)):
            if self._params['queue'] != 'debug':
                while os.path.isfile("run.%02d"% i):
                    i += 1

            exeoutput = "%s.%02d.out"%(exeoutput_pre, i)
            #if i:
            #    print "Warning: Executable output file(%s) already exists, reset to ."% exeoutput

            self._params['exeoutput'] = exeoutput

    def validate_queue(self, host):
        time = self._params['time']
        queue = self._params['queue']
        if queue == 'debug':
            dir_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            self._workdir = os.path.join('debug', dir_time)
        if host == "Cades":
            self._validate_queue_cades(queue, time)
        elif host == "BlueWaters":
            self._validate_queue_bw(queue, time)
        elif host == "Titan":
            self._validate_queue_titan(queue, time)
        else:
            msg = "Unknown host: %s, exit"% host
            self.setting_error(msg)

    def validate_depend(self, job_ids):
        dep_crit, dep_jobs = self._params['depend']
        if dep_crit in ['after', 'afterok', 'afterany', 'afternotok', 'before', 'beforeany', 'beforeok', 'beforenotok', 'on', 'synccount', 'syncwith']:
            msg = "Unrecognized dependency: %s, exit"% dep_crit
            self.setting_error(msg)
        # check if those jobs belongs to myself
        for job in dep_jobs:
            pass

    def _validate_queue_cades(self, queue, time):
        all_queues = ['std', 'long']
        if (queue.lower() != 'auto') and (queue not in all_queues):
            msg = "Queue error, exit."
            self.setting_error(msg)
        # only difference is that debug will run jobs in sub directories
        if queue.lower() == 'debug' or queue.lower() == 'auto':
            if time[0] > 48:
                queue = all_queues[1]
                #print "Walltime exceeds 48 hrs, queue is set to %s.\n"% queue
            else:
                queue = all_queues[0]
                #print "Walltime is under 48 hrs, queue is set to %s.\n"% queue
        self._params['queue'] = queue

    def _validate_queue_titan(self, queue, time):
        all_queues = ['batch', 'debug', 'killable']
        if queue.lower() == "debug":
            queue = all_queues[1]
        else:
            queue = all_queues[0]
        self._params['queue'] = queue

    def _validate_queue_bw(self, queue, time):
        all_queues = ['debug', 'normal', 'high']
        if queue != 'auto' and queue not in all_queues:
            msg = "Queue error, exit."
            pbs_conf.setting_error(msg)
        # ignore if queue is high
        if queue.lower() == 'high':
            pass
        elif queue.lower() == 'debug' or queue.lower() == 'auto':
            if time[0]*60+time[1] <= 30:
                queue = all_queues[0]
                #print "Walltime is under 30 mins, queue is set to %s.\n"% queue
            else:
                queue = all_queues[1]
                # print "Walltime exceeds 30 mins, queue is set to %s.\n"% queue
        self._params['queue'] = queue

def write_pbs(init_env, pbs_conf):
    threads  = pbs_conf._params['threads']
    nodes    = pbs_conf._params['nodes']
    time     = pbs_conf._params['time']
    name     = pbs_conf._params['name']
    queue    = pbs_conf._params['queue']
    exepath  = pbs_conf._params['exepath']
    account  = pbs_conf._params['account']
    exeinput = pbs_conf._params['exeinput']
    exeoutput= pbs_conf._params['exeoutput']
    exename  = pbs_conf._params['exename']
    cores    = pbs_conf._params['cores']
    module   = pbs_conf._params['module']
    depend = pbs_conf._params['depend']

    # convert to pbs format
    pwd         = os.path.join(init_env.get_pwd(), pbs_conf._workdir)
    if init_env.get_host().lower() == "titan":
        ppn_use     = divmod(16, threads)[0]
    else:
        ppn_use     = divmod(32, threads)[0]
    time_pbs    = "%02d:%02d:00"%(time[0], time[1])

    module_pbs = ""
    for _module in module:
        module_pbs += "module load %s\n"%_module

    pbs_dict = {'queue':        queue,
                'time':         time_pbs,
                'nodes':        nodes,
                'name':         name,
                'threads':      threads,
                'pwd':          pwd,
                'exename':      exename,
                'cores':        cores,
                'exepath':      exepath,
                'account':      account,
                'exeinput':     exeinput,
                'module':       module_pbs,
                'exeoutput':    exeoutput,
                'depend':       depend,
                'ppn_use':      ppn_use}

    if init_env.get_host() == "Cades":
        from hosts import cades
        lines_pbs = cades.get_pbs_lines(pbs_dict)

    elif init_env.get_host() == "BlueWaters":
        from hosts import bluewaters
        lines_pbs = bluewaters.get_pbs_lines(pbs_dict)

    elif init_env.get_host() == "Titan":
        from hosts import titan
        lines_pbs = titan.get_pbs_lines(pbs_dict)

    with open(os.path.join(pwd, 'pbs.%s'% exename.lower()), 'wb') as f:
        f.write(lines_pbs)

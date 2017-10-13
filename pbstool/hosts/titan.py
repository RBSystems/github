def get_pbs_lines(pbs_dict):
    exename = pbs_dict['exename']

    lines_pbs = ""
    lines_pbs += "#!/bin/bash\n"
    lines_pbs += "\n"
    lines_pbs += "#PBS -A %(account)s\n"% pbs_dict
    lines_pbs += "#PBS -q %(queue)s\n"% pbs_dict
    lines_pbs += "#PBS -m ea\n"
    lines_pbs += "#PBS -M zjyx147@foxmail.com\n"
    lines_pbs += "#PBS -j oe\n"
    lines_pbs += "#PBS -o out.$PBS_JOBID\n"
    lines_pbs += "#PBS -l walltime=%(time)s\n"% pbs_dict
    lines_pbs += "#PBS -l nodes=%(nodes)d\n"% pbs_dict
    lines_pbs += "#PBS -N %(name)s\n"% pbs_dict
    lines_pbs += "\n"
    lines_pbs += "source $MODULESHOME/init/bash\n"
    if exename == "RMG":
        lines_pbs += "module swap PrgEnv-pgi PrgEnv-gnu\n"
    elif exename == "QE":
        lines_pbs += "module swap PrgEnv-pgi PrgEnv-intel\n"
    lines_pbs += "module list\n"
    lines_pbs += "\n"
    lines_pbs += "setenv OMP_NUM_THREADS %(threads)d\n"% pbs_dict
    lines_pbs += "\n"
    lines_pbs += "\n"
    lines_pbs += "cd %(pwd)s\n"% pbs_dict
    lines_pbs += "\n"
    lines_pbs += "date\n"
    lines_pbs += "\n"
    if exename == "RMG":
        lines_pbs += "aprun -n %(cores)d -N %(ppn_use)d -d %(threads)d %(exepath)s %(exeinput)s > %(exeoutput)s\n"% pbs_dict
    elif exename == 'QE':
        lines_pbs += "aprun -n %(cores)d -N %(ppn_use)d -d %(threads)d %(exepath)s < %(exeinput)s > %(exeoutput)s\n"% pbs_dict
    lines_pbs += "\n"
    lines_pbs += "date\n"

    return lines_pbs

def get_all_queues():
    return ['debug', 'batch', 'killable']

def get_queue_threshold():
    return 30

def get_pbs_lines(pbs_dict):
    exename = pbs_dict['exename']

    lines_pbs = ""
    lines_pbs += "#!/bin/bash\n"
    lines_pbs += "\n"
    lines_pbs += "#PBS -A baec\n"
    lines_pbs += "#PBS -q %(queue)s\n"% pbs_dict
    lines_pbs += "#PBS -m ea\n"
    lines_pbs += "#PBS -M zjyx147@foxmail.com\n"
    lines_pbs += "#PBS -j oe\n"
    lines_pbs += "#PBS -o oe.$PBS_JOBID\n"
    lines_pbs += "#PBS -l walltime=%(time)s\n"% pbs_dict
    lines_pbs += "#PBS -l nodes=%(nodes)d:ppn=32:xe\n"% pbs_dict
    lines_pbs += "#PBS -N %(name)s\n"% pbs_dict
    lines_pbs += "\n"
    lines_pbs += "source /opt/modules/default/init/bash\n"
    if exename == "RMG":
        lines_pbs += "module swap PrgEnv-cray PrgEnv-gnu\n"
    elif exename == "QE":
        lines_pbs += "module swap PrgEnv-cray PrgEnv-gnu\n"
    lines_pbs += "module list\n"
    lines_pbs += "\n"
    lines_pbs += "export OMP_NUM_THREADS=%(threads)d\n"% pbs_dict
    lines_pbs += "\n"
    if exename == "RMG":
        lines_pbs += "export MPICH_MAX_THREAD_SAFETY=serialized\n"
        lines_pbs += "export OMP_WAIT_POLICY=passive\n"
        lines_pbs += "export MPICH_ENV_DISPLAY=1\n"
        lines_pbs += "export MPICH_ALLREDUCE_NO_SMP=1\n"
        lines_pbs += "ulimit -a\n"
        lines_pbs += "export CRAY_CUDA_PROXY=1\n"
        lines_pbs += "export MPICH_UNEX_BUFFER_SIZE=362914560\n"
        lines_pbs += "export MPICH_MAX_SHORT_MSG_SIZE=3200\n"
        lines_pbs += "\n"
    lines_pbs += "cd %(pwd)s\n"% pbs_dict
    lines_pbs += "\n"
    lines_pbs += "date\n"
    lines_pbs += "\n"
    if exename == "RMG":
        lines_pbs += "aprun -n %(cores)d -N %(ppn_use)d -d %(threads)d -cc numa_node %(exepath)s %(exeinput)s > %(exeoutput)s\n"% pbs_dict
    elif exename == 'QE':
        lines_pbs += "aprun -n %(cores)d -N %(ppn_use)d -d %(threads)d -cc numa_node %(exepath)s < %(exeinput)s > %(exeoutput)s\n"% pbs_dict
    elif exename == 'VASP':
        lines_pbs += "aprun -n %(cores)d -N %(ppn_use)d -d %(threads)d -cc numa_node %(exepath)s\n"% pbs_dict
    lines_pbs += "wait\n"
    lines_pbs += "\n"
    lines_pbs += "date\n"

    return lines_pbs

def get_all_queues():
    return ['debug', 'normal', 'high']

def get_queue_threshold():
    return 30

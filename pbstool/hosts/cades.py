def get_pbs_lines(pbs_dict):
    exename = pbs_dict['exename']

    lines_pbs = ""
    lines_pbs += "#! /bin/bash\n"
    lines_pbs += "\n"
    lines_pbs += "#PBS -A sns\n"
    #lines_pbs += "#PBS -q %(queue)s\n"% pbs_dict
    lines_pbs += "#PBS -q batch\n"
    lines_pbs += "#PBS -m ea\n"
    lines_pbs += "#PBS -M zjyx147@foxmail.com\n"
    lines_pbs += "#PBS -j oe\n"
    lines_pbs += "#PBS -o oe.$PBS_JOBID\n"
    lines_pbs += "#PBS -l qos=%(queue)s\n"% pbs_dict
    lines_pbs += "#PBS -W group_list=cades-virtues\n"
    if pbs_dict['depend'][0]:
        lines_pbs += "#PBS -W depend=%s:%d\n"% (pbs_dict['depend'][0], pbs_dict['depend'][1][0])
    lines_pbs += "#PBS -l walltime=%(time)s\n" % pbs_dict
    lines_pbs += "#PBS -l nodes=%(nodes)d:ppn=32\n"% pbs_dict
    lines_pbs += "#PBS -N %(name)s\n" % pbs_dict
    lines_pbs += "\n"
    lines_pbs += "%(module)s"% pbs_dict
    lines_pbs += "module list\n"
    lines_pbs += "\n"
    #lines_pbs += "ulimit -s unlimited\n"
    lines_pbs += "export OMP_NUM_THREADS=%(threads)d\n"% pbs_dict
    lines_pbs += "\n"
    lines_pbs += "cd %(pwd)s\n"% pbs_dict
    lines_pbs += "\n"
    lines_pbs += "date\n"
    lines_pbs += "\n"
    if exename == 'RMG':
        lines_pbs += "mpirun -np %(cores)d --bind-to none --map-by ppr:%(ppn_use)d:node:pe=%(threads)d %(exepath)s %(exeinput)s > %(exeoutput)s\n"% pbs_dict
        lines_pbs += "\n"
        lines_pbs += "if [ -f core ]; then\n"
        lines_pbs += "  rm core\n"
        lines_pbs += "fi\n"
        lines_pbs += "if [ ! `grep TIMING oe.$PBS_JOBID *log` = '' ]; then\n"
        lines_pbs += "  exit -1\n"
        lines_pbs += "fi\n"
    elif exename == 'QE':
        lines_pbs += "mpirun -np %(cores)d --bind-to none --map-by ppr:%(ppn_use)d:node:pe=%(threads)d %(exepath)s < %(exeinput)s > %(exeoutput)s\n"% pbs_dict
    elif exename == 'VASP':
        lines_pbs += "mpirun -np %(cores)d --bind-to none --map-by ppr:%(ppn_use)d:node:pe=%(threads)d %(exepath)s\n"% pbs_dict
        lines_pbs += '\n'
        lines_pbs += "if [ ! `grep WARNING oe.$PBS_JOBID OUTCAR` = '' ]; then\n"
        lines_pbs += "  grep WARNING oe.$PBS_JOBID OUTCAR >> WARNING\n"
        lines_pbs += "  exit 2013\n"
        lines_pbs += "fi\n"
    elif exename == 'CASTEP':
        lines_pbs += "PSPOT_DIR=/software/user_tools/current/cades-virtues/apps/castep/pseudopotentials\n"
        lines_pbs += "export PSPOT_DIR\n"
        lines_pbs += '\n'
        lines_pbs += "mpirun -np %(cores)d --bind-to none --map-by ppr:%(ppn_use)d:node:pe=%(threads)d %(exepath)s %(exeinput)s\n"% pbs_dict
    lines_pbs += "\n"
    lines_pbs += "date\n"
    lines_pbs += '\n'

    return lines_pbs

def get_all_queues():
    return ['batch', 'long']

def get_queue_threshold():
    return 30

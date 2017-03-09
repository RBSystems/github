def get_pbs_lines(pbs_conf, pbs_dict):
    lines_pbs = ""
    lines_pbs += "#!/bin/bash\n"
    lines_pbs += "\n"
    lines_pbs += "#PBS -A sns\n"
    lines_pbs += "#PBS -q %(queue)s\n"% pbs_dict
    lines_pbs += "#PBS -m ea\n"
    lines_pbs += "#PBS -M zjyx1991@foxmail.com\n"
    lines_pbs += "#PBS -j oe\n"
    lines_pbs += "#PBS -l qos=condo\n"
    lines_pbs += "#PBS -W group_list=cades-virtues\n"
    lines_pbs += "#PBS -l walltime=%(time)s\n" % pbs_dict
    lines_pbs += "#PBS -l nodes=%(nodes)d:ppn=32\n"% pbs_dict
    lines_pbs += "#PBS -N %(name)s\n" % pbs_dict
    lines_pbs += "\n"
    lines_pbs += "%(module)s"% pbs_dict
    lines_pbs += "module list\n"
    lines_pbs += "\n"
    lines_pbs += "export OMP_NUM_THREADS=%(threads)d\n"% pbs_dict
    lines_pbs += "\n"
    lines_pbs += "cd %(pwd)s\n"% pbs_dict
    lines_pbs += "\n"
    lines_pbs += "date\n"
    lines_pbs += "\n"
    if exename == 'RMG':
        lines_pbs += "mpirun -np %(cores)d --bind-to none --map-by ppr:%(ppn_use)d:node:pe=%(threads)d %(exepath)s %(exeinput)s > %(exeoutput)s\n"% pbs_dict
    elif exename == 'QE':
        lines_pbs += "mpirun -np %(cores)d --bind-to none --map-by ppr:%(ppn_use)d:node:pe=%(threads)d %(exepath)s < %(exeinput)s > %(exeoutput)s\n"% pbs_dict
    elif exename == 'VASP':
        lines_pbs += "mpirun -np %(cores)d --bind-to none --map-by ppr:%(ppn_use)d:node:pe=%(threads)d %(exepath)s\n"% pbs_dict
    lines_pbs += "\n"
    lines_pbs += "date\n"

    return lines_pbs

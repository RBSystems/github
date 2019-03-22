#! /bin/bash

#PBS -q std
#PBS -m bea
#PBS -M zjyx147@foxmail.com
#PBS -j oe
#PBS -o oe.$PBS_JOBID
#PBS -l walltime=1000:00:00
#PBS -N arch-data

echo -e "\n-----------------------------------------------------------------------"
echo -e " Environment variables:"
echo -e "-----------------------------------------------------------------------\n\n\n"
printenv
echo -e "\n-----------------------------------------------------------------------\n\n\n"

#export OMP_NUM_THREADS=1

#cd /lustre/or-hydra/cades-virtues/z8j/run/ZrH2/vasp/supercell/disps/disp-001/
cd $PBS_O_WORKDIR

date

#mv fropho_calc/ /home/zjyx/data_drive/data-archived/ZrH2/
#cp pbs.sh /home/zjyx/data_drive/data-archived/ZrH2/
echo -e "\n-----------------------------------------------------------------------"
echo -e " stdout + stderr:"
echo -e "-----------------------------------------------------------------------\n\n\n"
tar zcvf frophon.tgz fropho_calc
echo -e "\n-----------------------------------------------------------------------\n\n\n"
wait

date


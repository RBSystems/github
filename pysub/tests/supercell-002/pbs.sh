#! /bin/bash

#PBS -A sns
#PBS -q batch
#PBS -m ea
#PBS -M zjyx147@foxmail.com
#PBS -j oe
#PBS -l qos=long
#PBS -W group_list=cades-virtues
#PBS -l walltime=48:00:00
#PBS -l nodes=8:ppn=32
#PBS -N carb-disp.001@/lustre/or-hydra/cades-virtues/z8j/run/Carbazole/rmg/test2/supercell/supercells/supercell-001

module load PE-gnu
module list

export OMP_NUM_THREADS=1

cd /lustre/or-hydra/cades-virtues/z8j/run/Carbazole/rmg/test2/supercell/supercells/supercell-001

date

mpirun -np 256 --bind-to none --map-by ppr:32:node:pe=1 /home/z8j/softwares/rmg-4042/rmg-cpu supercell.in > supercell.00.out

date

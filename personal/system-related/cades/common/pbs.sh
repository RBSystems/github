#! /bin/bash

#PBS -A sns
#PBS -q batch
#PBS -m ea
#PBS -M zjyx147@foxmail.com
#PBS -j oe
#PBS -o oe.$PBS_JOBID
#PBS -l qos=std
#PBS -W group_list=cades-virtues
#PBS -l walltime=10:00:00
#PBS -l nodes=1:ppn=32
#PBS -N test

module list

export OMP_NUM_THREADS=1

cd $PBS_O_WORKDIR

date

./out

date

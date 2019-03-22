#! /bin/bash

rmg_input=unitcell.in
qe_input=qe.in
vasp_input=POSCAR-unitcell

# generate supercells for RMG, pwscf

if [ -e $rmg_input ]; then
    mode=rmg
    input=$rmg_input
elif [ -e $qe_input ]; then
    mode=pwscf
    input=$qe_input
elif [ -e $vasp_input ]; then
    mode=vasp
    input=$vasp_input
else
    echo -e "No default unitcell file found.\n"
    exit 1
fi

python /home/zjyx/softwares/phonopy-1.10.10/bin/phonopy --$mode -c $input -d --dim="2 2 2"

exit 0

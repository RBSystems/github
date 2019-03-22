#!/bin/bash

# plot band structure 

if [ -e unitcell.in ]; then
    mode=rmg
    input=unitcell.in
elif [ -e qe.in ]; then
    mode=pwscf
    input=qe.in
elif [ -e POSCAR-unitcell ]; then
    mode=vasp
    input=POSCAR-unitcell
else
    echo -e "No default unitcell file found.\n"
    exit 1
fi

python /home/zjyx/softwares/phonopy-1.10.10/bin/phonopy --$mode -c $input -s -p band.conf

exit 0

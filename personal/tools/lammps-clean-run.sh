#!/bin/bash
# program: to clean lammps log files

# files to be removed
lammps_run_trash="
lammps.in.*
md.in.*
supercell.in.*
*.o*[0-9]*
*[0-9]*OU
run.*[0-9]*
run.*[0-9]*
*.*[0-9]*.out
core
Wave*
oe.*
log.lammps
"

#################################################
#
# Following lines should not be modified
#
#################################################

function lammps_run_clean()
{
    if [ -e $* ]; then
        rm -rf $*
        echo -e "$* removed.\n"
    fi
}

echo -e "\nCleaning Lammps previous run files...\n"

for tmp in $lammps_run_trash
do
    lammps_run_clean $tmp
done

exit 0

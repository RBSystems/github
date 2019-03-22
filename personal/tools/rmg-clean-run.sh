#!/bin/bash
# program: to clean rmg log files

# files to be removed
rmg_run_trash="
rmg.in.*
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
"

#################################################
#
# Following lines should not be modified
#
#################################################

function rmg_run_clean()
{
    if [ -e $* ]; then
        rm -rf $*
        echo -e "$* removed.\n"
    fi
}

echo -e "\nCleaning RMG previous run files...\n"

for tmp in $rmg_run_trash
do
    rmg_run_clean $tmp
done

exit 0

#!/bin/bash
# program: to clean cp2k log files

# files to be removed
cp2k_run_trash="
oe.*[0-9]*
*restart*
*RESTART*
*out
*.*[0-9]*.out
run.*[0-9]*
output_dir
*Hessian
*pos*xyz
"

#################################################
#
# Following lines should not be modified
#
#################################################

function cp2k_run_clean()
{
    if [ -e $* ]; then
        rm -rf $*
        echo -e "$* removed."
    fi
}

echo -e "\nCleaning CP2K previous run files...\n"

for tmp in $cp2k_run_trash
do
    cp2k_run_clean $tmp
done

exit 0

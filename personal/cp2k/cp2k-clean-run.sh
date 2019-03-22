#!/bin/bash
# program: to clean rmg log files

# files to be removed
cp2k_run_trash="
*.o*[0-9]*
run.*[0-9]*
*.*[0-9]*.out
core
oe.*
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
        echo -e "$* removed.\n"
    fi
}

echo -e "\nCleaning previous CP2K run files...\n"

for tmp in $cp2k_run_trash
do
    cp2k_run_clean $tmp
done

exit 0

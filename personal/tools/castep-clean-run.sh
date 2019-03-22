#!/bin/bash
# program: to clean rmg log files

# files to be removed
castep_run_trash="
*.o*[0-9]*
run.*[0-9]*
*.*[0-9]*.err
*.check
*.castep_bin
*.bands
*bib
*cst_esp
*geom
*phonon
*check_bak
*dfpt_*
"

#################################################
#
# Following lines should not be modified
#
#################################################

function castep_run_clean()
{
    if [ -e $* ]; then
        rm -rf $*
        echo -e "$* removed.\n"
    fi
}

echo -e "\nCleaning CASTEP previous run files...\n"

for tmp in $castep_run_trash
do
    castep_run_clean $tmp
done

exit 0

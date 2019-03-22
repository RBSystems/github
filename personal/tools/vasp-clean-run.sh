#!/bin/bash
# program: clean up vasp run files

# files to be removed
vasp_run_trash="
CHG
CHGCAR
CONTCAR
DOSCAR
EIGENVAL
IBZKPT
ICONST
OSZICAR
OUTCAR
PCDAT
REPORT
WAVECAR
XDATCAR
vasprun.xml
*.o*[0-9]*
run*[0-9]*
"

#################################################
# Following lines should not be modified
#################################################

function vasp_run_clean()
{
    if [ -e $* ]; then
        rm -rf $*
        echo -e "$* removed.\n"
    fi
}

echo -e "\nCleaning up VASP previous run files...\n"

for tmp in $vasp_run_trash
do
    vasp_run_clean $tmp
done

exit 0

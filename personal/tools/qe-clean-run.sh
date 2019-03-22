#!/bin/bash
# program: to clean qe log files

# files to be removed
qe_run_trash="
qe*out*
*.o*[0-9]*
runenv.*[0-9]*
core
input_tmp.in
CRASH
*.*[0-9]*.out
run.*[0-9]*
output_dir
"

#################################################
#
# Following lines should not be modified
#
#################################################

function qe_run_clean()
{
    if [ -e $* ]; then
        rm -rf $*
        echo -e "$* removed.\n"
    fi
}

echo -e "\nCleaning QE previous run files...\n"

for tmp in $qe_run_trash
do
    qe_run_clean $tmp
done

exit 0

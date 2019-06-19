#! /bin/bash

done_signal=DONE
log_file=*out
my_pwd=`pwd`

all_dir=`ls -l | egrep '^d' | awk '{print $9}'`

for dir in $all_dir
do
this_path="$my_pwd/$dir/$log_file"
if ! grep -q $done_signal $this_path ; then
#if ! [ `grep "$done_signal" $this_path` ] ; then
    echo ${dir}
fi
done

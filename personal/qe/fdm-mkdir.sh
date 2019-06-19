#! /bin/bash

job_sh='lsf.sh'

all_files="
supercell*in
$job_sh
"

function qe_check_input_file()
{
    if [ ! -e $* ]; then
        echo -e "$* not found! Exit.\n"
        exit 1
    fi
}


for this_file in $all_files
do
    qe_check_input_file $this_file
done

if [ ! -d "disps" ]; then
    mkdir "disps"
fi

i=0

if [ -e supercell.in ]; then
    mv supercell.in supercell-000.in
fi

while [ -e `printf "supercell-%03d.in" $i` ]; do
    this_dir=`printf "disps/disp-%04d" $i`
    this_input=`printf "supercell-%03d.in" $i`

    if [ ! -d $this_dir ]; then
        mkdir $this_dir
    fi

    cp "./$job_sh" "$this_dir/$job_sh"
    sed -i "s/null/$i/g" "$this_dir/$job_sh"

    cat header $this_input > "$this_dir/supercell.in"
    rm $this_input

    ((i=i+1))
done

exit 0

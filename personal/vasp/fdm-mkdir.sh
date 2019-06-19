#! /bin/bash

all_files="
INCAR
POTCAR
KPOINTS
pbs.vasp
"

function vasp_check_input_file()
{
    if [ ! -e $* ]; then
        echo -e "$* not found! Exit.\n"
        exit 1
    fi
}


for this_file in $all_files
do
    vasp_check_input_file $this_file
done

if [ ! -d "disps" ]; then
    mkdir "disps"
fi

i=0
cp SPOSCAR POSCAR-000
while [ -e `printf "POSCAR-%03d" $i` ]; do
    this_dir=`printf "disps/disp-%03d" $i`
    this_POSCAR=`printf "POSCAR-%03d" $i`

    if [ ! -d $this_dir ]; then
        mkdir $this_dir
    fi

    for this_file in $all_files
    do
        cp $this_file $this_dir
    done
    mv "$this_dir/pbs.vasp" "$this_dir/pbs.sh"
    sed -i "s/null/$i/g" "$this_dir/pbs.sh"
    #sed -i "/^#PBS -N/ s/$/$i/" "$this_dir/pbs.sh"
    mv $this_POSCAR "$this_dir/POSCAR"

    ((i=i+1))
done

exit 0

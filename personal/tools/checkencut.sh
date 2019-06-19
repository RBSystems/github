#!/bin/sh

function createENCUT()
{
    dir_name=encut-$1
    if [ ! -e $dir_name ]; then
        mkdir $dir_name
    fi
    if grep -q null $dir_name/INCAR; then
        echo -e "Error find null in INCAR.\n"
        exit
    fi
    cp POTCAR KPOINTS INCAR POSCAR pbs.vasp $dir_name;
    sed -i "s/null/$i/g" $dir_name/INCAR
    sed -i "s/null/$i/g" $dir_name/pbs.vasp
}

function getEnergy()
{
    encut=$1
    E=`grep "TOTEN" encut-$i/OUTCAR | tail -1 | awk '{printf "%12.6f \n", $5 }'`#
    echo $encut $E >> result
}

for i in {300..1000..50}
do
echo "ENCUT = $i";
#createENCUT $i
getEnergy $i
done

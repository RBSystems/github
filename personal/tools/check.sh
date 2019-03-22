#!/bin/sh

function createKPT()
{
    dir_name=kpt-$1
    if [ ! -e $dir_name ]; then
        mkdir $dir_name
    fi
    cp POTCAR POSCAR INCAR pbs.vasp $dir_name;
    cat > $dir_name/KPOINTS <<EOF
Automatic generation
0
G
$i $i $i
0 0 0
EOF
}

function getEnergy()
{
    nkpt=$1
    E=`grep "TOTEN" kpt-$i/OUTCAR | tail -1 | awk '{printf "%12.6f \n", $5 }'`
    KP=`grep "irreducible" kpt-$i/OUTCAR | tail -1 | awk '{printf "%5i \n", $2 }'`
    echo $nkpt $KP $E >> result
}

for i in 1 2 3 4 5 6 7 8 9
do
echo "k mesh = $i x $i x $i";
#createKPT $i;
getEnergy $i;
done

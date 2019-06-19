#!/bin/sh

function createKPT()
{
    dir_name=kpt-$1
    if [ ! -e $dir_name ]; then
        mkdir $dir_name
    fi
    cp POTCAR POSCAR INCAR pbs.vasp $dir_name;
    sed -i "s/null/$i/g" $dir_name/pbs.vasp;
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

for i in {1..15}
do
echo "k mesh = $i x $i x $i";
#createKPT $i
getEnergy $i
done

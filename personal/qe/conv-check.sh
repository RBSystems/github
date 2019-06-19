#!/bin/sh

mode="encut" #encut or kpt
min=40
max=100
step=10

function createENCUT()
{
    dir_name=encut-$1
    if [ ! -e $dir_name ]; then
        mkdir $dir_name
    fi
    cp qe.in lsf.sh $dir_name;
    sed -i "s/ecutwfc.*/ecutwfc = $1/g" $dir_name/qe.in; 
    sed -i "s/ecutrho.*/ecutrho = $((4*$1))/g" $dir_name/qe.in; 
    sed -i "s/null/$ix$ix$i/g" $dir_name/lsf.sh; 
}

function createKPT()
{
    dir_name=kpt-$1
    if [ ! -e $dir_name ]; then
        mkdir $dir_name
    fi
    cp qe.in lsf.sh $dir_name;
    sed -i "s/3 3 3/$i $i $i/g" $dir_name/qe.in; 
    sed -i "s/null/$ix$ix$i/g" $dir_name/lsf.sh; 
}

function getKPTEnergy()
{
    nkpt=$1
    E=`grep "!    total energy" kpt-$i/qe.out | tail -1 | awk '{printf "%12.6f \n", $5 }'`#
    KP=`grep "k points" kpt-$i/qe.out | tail -1 | awk '{printf "%5i \n", $5 }'`
    FORCE=`grep "Total force" kpt-$i/qe.out | tail -1 | awk '{printf "%12.6f \n", $4 }'`
    echo $nkpt $KP $FORCE $E >> result
}

function getENCUTEnergy()
{
    encut=$1
    E=`grep "!    total energy" encut-$i/qe.out | tail -1 | awk '{printf "%12.6f \n", $5 }'`#
    FORCE=`grep "Total force" encut-$i/qe.out | tail -1 | awk '{printf "%12.6f \n", $4 }'`
    echo $encut $FORCE $E >> result
}

if [ "$mode" = 'encut' ]; then
    if [ -e result ]; then
        rm result;
        echo -e "# encut; total force (Ryd/Bohr); total energy (Ryd)\n" >> result
    fi
    for i in $(seq $min $step $max)
    #for i in {${min}..${max}..${step}}
    do
    echo "ENCUT = $i Ryd";
    #createENCUT $i
    getENCUTEnergy $i
    done
elif [ "$mode" = 'kpt' ]; then
    if [ -e result ]; then
        rm result;
        echo -e "# mesh; number of Kpoints; total force (Ryd/Bohr); total energy (Ryd)\n" >> result
    fi
    for i in {$(min)..$(max)..$(step)}
    do
    echo "k mesh = $i x $i x $i";
    createKPT $i
    #getKPTEnergy $i
    done
fi

#!/bin/bash
# To Use it： potcar.sh Cu C H O
# TODO:
#       1. add support for adding pp type

# Define local potpaw_GGA pseudopotential repository:
repo="/home/z8j/github-ncsu/personal/vasp/pp/PAW_PBE/"

argn=$#
if [ "$argn" -lt "1" ] ; then
    echo "Error: no elements specified."
    exit 1
fi

# Check if older version of POTCAR is present
if [ -f POTCAR ] ; then
    mv -f POTCAR old-POTCAR
    echo "Warning: old POTCAR file found and renamed to 'old-POTCAR'."
fi

# Main loop - concatenate the appropriate POTCARs (or archives)
for i in $*
do
 if test -f $repo/$i/POTCAR ; then
    cat $repo/$i/POTCAR>> POTCAR
 elif test -f $repo/$i/POTCAR.Z ; then
    zcat $repo/$i/POTCAR.Z >> POTCAR
 elif test -f $repo/$i/POTCAR.gz ; then
    gunzip -c $repo/$i/POTCAR.gz >> POTCAR
 else
    echo "Warning: No suitable POTCAR for element '$i' found!! Skipped this element."
 fi
done

#echo -n "Max ENCUT among all elements:"
echo -n "Elements in order with orbitals:"
echo -n `grep VRHFIN POTCAR | awk -F= '{printf" %s", $2}'`
echo -e ""
echo -e `grep ENMAX POTCAR | awk '{printf"%f\n", $3}' | awk '{if(min==""){min=max=$1}; if($1>max) {max=$1}; if($1<min) {min=$1}; total+=$1; count+=1} END {printf"Max ENCUT among all elements: %f eV (1.3X: %f eV)\n",max, 1.3*max}'`

exit 0

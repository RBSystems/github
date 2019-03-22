#/bin/bash

input=$1

g++ -fopenmp -o $input.out $input
if [ $? -eq 0 ]; then
    ./$input.out
fi

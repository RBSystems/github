#!/bin/bash

for ((i=100;i<1100;i=i+100))
do
cp phband.in phband_${i}K.in
sed -i "s/100K/${i}K/g" phband_${i}K.in
done

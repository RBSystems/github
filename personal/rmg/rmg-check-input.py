#! /usr/bin/env python

#check input parameters for RMG before running

# if restart, make sure that ./Waves exists.
# check PE, avoid number 3

import os
import sys

def check_good_number(i):

    

with open('rmg.in') as f:
    lines_in = f.readlines()



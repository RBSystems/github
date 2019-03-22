#!/bin/bash

~/github-ncsu/personal/alamode/tools/extract.py --RMG=rmg.in --get=disp *log > disp.dat
~/github-ncsu/personal/alamode/tools/extract.py --RMG=rmg.in --get=force *log > force.dat

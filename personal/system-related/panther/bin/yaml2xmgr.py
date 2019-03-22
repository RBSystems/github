#!/usr/bin/python2

import sys

dist = []
freq = []

with open('band.yaml') as f:
    lines = f.readlines()

for i in range(len(lines)):
    if 'q-position' in lines[i]:

        tmp_dist = lines[i+1].split()[1]
        dist.append(float(tmp_dist))

        freq.append([])
        while 1:
            if len(lines[i]) < 2:
                break
            if 'frequency' in lines[i]:
                tmp_freq = lines[i].split()[1]
                freq[-1].append(float(tmp_freq))
            i += 1
            if i == len(lines):
                break

f = open('freq.xmgr','w')

lines_w = ""
if len(dist) != len(freq):
    print ('Error! Dimension of distances and frequncies do not match!\n')
    sys.exit(1)

for i in range(len(freq[0])):
    for j in range(len(dist)):
        lines_w += '%12.7f     %12.7f\n'%(dist[j], freq[j][i])
    lines_w += '&\n'

f.write(lines_w)
f.close()

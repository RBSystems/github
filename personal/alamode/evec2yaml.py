#!/usr/bin/env python
'''
    description:
        convert alamode evec file to yaml file
    input:
        .evec
    output:
        .yaml
    usage:
        python evec2yaml.py [basename]
'''



import numpy as np
import cmath
import os
import sys
# units of lattic
# eigevec is normalized


if len(sys.argv) > 1:
    basename = sys.argv[1]
else:
    print('Error: a base name must be provided.\n')
    sys.exit(1)


filename = basename + '.evec'
yamlfile = basename+'.yaml'

#vec2cm = 3.2170*10000/(2*3.1415927) # in units of cm-1
factor_freq = 3287.566026 #in units of THz
bohr2angst = 0.529177


nqpoint = 0
natom = 0
lattice = []
atoms = []
phonon = []
q_position = []
band = []
mass = {}
freq = []

with open(filename, 'rb') as f:
    inlines = f.readlines()

for i in range(len(inlines)):
    if 'Number of k points' in inlines[i]:
        nqpoint = int(inlines[i].split()[-1])
    elif 'Number of phonon modes' in inlines[i]:
        natom = int(int(inlines[i].split()[-1])/3)
    elif "Lattice vectors" in inlines[i]:
        for j in range(3):
            tmp = map(float, inlines[i+1+j].split()) 
            lattice.append(tmp)
    elif "Eigenvalues and eigenvectors" in inlines[i]:
        phonon_start = i
        break 

for i in range(phonon_start, len(inlines)):
    if 'kpoint' in inlines[i]:
        q_position.append(map(float, inlines[i].split()[4:7]))
        band.append([])
        freq.append([])
        for j in range(i+1, len(inlines)):
            if 'mode' in inlines[j]:
                band[-1].append([])
                freq[-1].append(float(inlines[j].split()[-1]))
            elif 'kpoint' in inlines[j]:
                break
            elif len(inlines[j]) > 1:
                band[-1][-1].append(map(float, inlines[j].split()))

# read atom symbols
if os.path.isfile('dos.out'):
    with open('dos.out') as f:
        alllines = f.readlines()

    for i in range(len(alllines)):
        if "Atomic positions" in alllines[i]:
            for j in range(i+1, i+1+natom):
                atoms.append([])
                atoms[-1].append(alllines[j].split()[-1])
                atoms[-1].append(map(float, alllines[j].split()[1:4]))
                #atoms[alllines[j].split()[-1]] = [ 0, 0.0, []]
                #atoms[alllines[j].split()[-1]][2] = alllines[j].split()[1:4]
                #atoms[alllines[j].split()[-1]][0] = alllines[j].split()[0].rstrip(':')
            break

    # read mass
    for i in range(len(alllines)):
        if "Mass of" in alllines[i]:
            for j in range(i+1, i+1+natom):
                #atoms[j-i-1].append(float(alllines[j].split()[1]))
                if len(alllines[j]) < 2:
                    break 
                mass[alllines[j].split()[0].rstrip(':')] = float(alllines[j].split()[1])
                #atoms[alllines[j].split()[0].rstrip(':')][1] = float(alllines[j].split()[1])

#print nqpoint, natom, lattice, q_position[0], band[0][-1], freq[0][-1]

mesh = int(np.cbrt(nqpoint))
if (mesh-np.cbrt(nqpoint))>1.0e-4:
    print "Warning: nqpoint is not a cubic number!\n"

outlines = ''
outlines += "mesh: [ %4d,%4d,%4d ]\n"%(mesh, mesh, mesh)
outlines += "nqpoint: %d\n"%nqpoint
outlines += "natom: %d\n"%natom
outlines += "lattice:\n"
outlines += "- [ %16.12f, %16.12f, %16.12f ]\n"%(tuple(bohr2angst*x for x in lattice[0]))
outlines += "- [ %16.12f, %16.12f, %16.12f ]\n"%(tuple(bohr2angst*x for x in lattice[1]))
outlines += "- [ %16.12f, %16.12f, %16.12f ]\n"%(tuple(bohr2angst*x for x in lattice[2]))
#outlines += "- [ %16.2f, %16.2f, %16.2f ]\n"%(lattice[1][0], lattice[1][1], lattice[1][2])
#outlines += "- [ %16.2f, %16.2f, %16.2f ]\n"%(lattice[2][0], lattice[2][1], lattice[2][2])
outlines += "atoms:"
for i in range(natom):
    outlines += '''
- symbol: %s # %d
  coordinates: [  %18.12f,  %18.12f,  %18.12f ]
  mass: %f'''%(atoms[i][0], i+1, atoms[i][1][0], atoms[i][1][1], atoms[i][1][2], mass[atoms[i][0]])
#- symbol: H  # 2
#  coordinates: [  0.500000000000000,  0.750000010000001,  0.250000010000001 ]
#  mass: 1.007940
#- symbol: H  # 3
#  coordinates: [  0.500000000000000,  0.250000010000001,  0.750000010000001 ]
#  mass: 1.007940
#'''
outlines += "\nphonon:\n"
for i in range(len(q_position)):
    outlines += "- q-position: [%12.7f, %12.7f, %12.7f ]\n"%tuple(q_position[i])
    outlines += '  weight: 1\n'
    outlines += '  band:\n'
    for j in range(len(band[0])):
        outlines += '  - # %d\n'%(j+1)
        outlines += '    frequency: %18.10f\n'%(factor_freq*cmath.sqrt(freq[i][j]).real)
        outlines += '    eigenvector:\n'
        for k in range(natom):
            outlines += '    - # atom %d\n'%(k+1)
            outlines += '      - [ %20.15f, %20.15f ]\n'%tuple(band[i][j][3*k+0])
            outlines += '      - [ %20.15f, %20.15f ]\n'%tuple(band[i][j][3*k+1])
            outlines += '      - [ %20.15f, %20.15f ]\n'%tuple(band[i][j][3*k+2])

    outlines += "\n"

with open(yamlfile, 'wb') as f:
    f.write(outlines)

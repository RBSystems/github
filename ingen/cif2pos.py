#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2011 Li Zhu <zhulipresent@gmail.com>
# Licensed under the GPL V3
# Version: 0.2.8
# update: 2011.4.6
# modified by zjyx at March/2016, ORNL

import os
import sys
import re
import math as m
import numpy as np
from fractions import Fraction as frac

def version():
    print 'cif -> POSCAR'
    print 'Version: 0.2.8'

def readfile(filename):
    ''' read file to a list; 
    and del blank lines'''
    try:
        f = open(filename)
    except:
        print('Error: cannot open file:'+ filename)
        sys.exit(1)
    rst = []
    for line in f:
        if len(line.strip()) != 0:
            rst.append(line.strip())
    f.close()

    return rst

def symmetry(cif):
    symm = []
    symmetry = []
    trans = []
    iline = 0
    for line in cif:
        iline += 1
        if '_symmetry_equiv_pos_as_xyz' in line or '_space_group_symop_operation_xyz' in line:
            for item in cif[iline:]:
                if item.strip()[0] != '_' and item.strip() != 'loop_':
                    if item[0] == "'" or item[0] == '"':
                        iitem = item[1:-1]
                    else:
                        iitem = item[:]
                    symm.append(iitem.strip().split(','))
                else:
                    break
            break

    for item in symm:
        s2 = []
        tran1 = []
        for subtem in item:
            subtem = subtem.strip()
            try:
                isprit = subtem.index('/')
                stt = [istr for istr in subtem]
                for i in range(0, 3): del(stt[isprit - 1])
                if stt[-1] == '+' or stt[-1] == '-': del(stt[-1])
                subt = ''.join(stt)
            except:
                subt = subtem[:]
            s1 = [0, 0, 0]
            if subt[0] == '-' or subt[0] == '+':
                for i in range(0, len(subt) - 1, 2):
                    if subt[i:i+2] == '-x': s1[0] = -1
                    if subt[i:i+2] == '+x': s1[0] = 1
                    if subt[i:i+2] == '-y': s1[1] = -1
                    if subt[i:i+2] == '+y': s1[1] = 1
                    if subt[i:i+2] == '-z': s1[2] = -1
                    if subt[i:i+2] == '+z': s1[2] = 1
            else:
                if subt[0] == 'x': s1[0] = 1
                if subt[0] == 'y': s1[1] = 1
                if subt[0] == 'z': s1[2] = 1
                for i in range(1, len(subt) - 1, 2):
                    if subt[i:i+2] == '-x': s1[0] = -1
                    if subt[i:i+1] == '+x': s1[0] = 1
                    if subt[i:i+2] == '-y': s1[1] = -1
                    if subt[i:i+2] == '+y': s1[1] = 1
                    if subt[i:i+2] == '-z': s1[2] = -1
                    if subt[i:i+2] == '+z': s1[2] = 1
            t1 = 0.
            for subsub in re.split('[+,-]', subtem):
                try:
                    t1 = float(frac(subsub))
                except:
                    continue
            tran1.append(t1)
            s2.append(s1)
        symmetry.append(s2)
        trans.append(tran1)
    return (np.array(symmetry), np.array(trans))


def atominfo(cif):

    loopinfo = []
    atominfo = []
    for i in range(0, len(cif)):
        if cif[i].strip() == 'loop_':
            istart = i
            loopinfo = []
            atominfo = []
            for j in range(istart + 1, len(cif)):
                if cif[j].strip() == 'loop_': break
                if cif[j].strip()[0] == '_':
                    loopinfo.append(cif[j].strip())
                else:
                    atominfo.append(cif[j].strip().replace('(','').replace(')',''))

        if '_atom_site_fract_x' in loopinfo: break

    try:
        il = loopinfo.index('_atom_site_label')
        ix = loopinfo.index('_atom_site_fract_x')
        iy = loopinfo.index('_atom_site_fract_y')
        iz = loopinfo.index('_atom_site_fract_z')
    except:
        print '2'
        exit(0)
    typesym = True
    try:
        it = loopinfo.index('_atom_site_type_symbol')
    except:
        typesym = False

    atomtmp = [a.split() for a in atominfo]
    print atominfo, atomtmp
    label = []
    ato = []
    symbol = []
    for item in atomtmp:
        label.append(item[il])
        ato.append(map(float, [item[ix],item[iy],item[iz]]))

    if typesym == True:
        for item in atomtmp:
            symbol.append(item[it])
    else:
        for lab in label:
            s = ''
            for i in range(0, len(lab)):
                try:
                    itmp = int(lab[i])
                except:
                    s += lab[i]
            symbol.append(s)

    equAtom = {}
    for i in range(0, len(label)):
        equAtom[label[i]] = [symbol[i], ato[i]]

    return equAtom

def lattice(cif):
    for item in cif:
        if "_cell_length_a" in item:
            a = float(item.split()[1].replace('(','').replace(')',''))
        if "_cell_length_b" in item:
            b = float(item.split()[1].replace('(','').replace(')',''))
        if "_cell_length_c" in item:
            c = float(item.split()[1].replace('(','').replace(')',''))
        if "_cell_angle_alpha" in item:
            alpha = float(item.split()[1])/180*m.pi
        if "_cell_angle_beta" in item:
            beta = float(item.split()[1])/180*m.pi
        if "_cell_angle_gamma" in item:
            gamma = float(item.split()[1])/180*m.pi

    bc2 = b**2 + c**2 - 2*b*c*m.cos(alpha)

    h1 = a
    h2 = b * m.cos(gamma)
    h3 = b * m.sin(gamma)
    h4 = c * m.cos(beta)
    h5 = ((h2 - h4)**2 + h3**2 + c**2 - h4**2 - bc2)/(2 * h3)
    h6 = m.sqrt(c**2 - h4**2 - h5**2)

    lattice = [[h1, 0., 0.], [h2, h3, 0.], [h4, h5, h6]]
    
    return lattice 

def optAtom(atom, symm, trans):
    a = np.mat(atom).transpose()
    alist = []
    for imat in symm:
        mat = np.mat(imat)
        ta = mat*a
        alist.append(ta.transpose().tolist()[0])
 
    slist = np.array(alist) + trans
    # debug
    # print '1111111111111111111111111'
    # print slist
    # enddebug
    for item in slist:
        for i in range(0, 3):
            item[i] = item[i] - int(item[i])
            if item[i] < 0.: item[i] += 1
            if item[i] >= 1.: item[i] -= 1
            if np.abs(np.abs(item[i]) - 1.0) < 1e-5: item[i] = 0.
    # debug
    # print '2222222222222222222222222'
    # print slist
    # enddebug
    
    badlist = [] 
    for i in range(0, len(slist)):
        for j in range(i + 1, len(slist)):
            dd = np.sqrt(sum((slist[i]-slist[j]) * (slist[i]-slist[j])))
            # print 'dd ', i,j,dd
            if abs(dd) < 1e-5: badlist.append(j)
    # print badlist
    rsl = []

    for i in range(0, len(slist)):
        if i not in badlist:
            rsl.append(slist[i])

    # debug
    # print '333333333333333333333333'
    # print np.array(rsl)
    # enddebug
    return np.array(rsl)

def p1atom(order, ea, symm, trans):
    p1 = []
    type = []
    k = ea.keys()
    for item in order:
        it = 0
        for ik in k:
            if ea[ik][0].lower() == item.lower():
                t = optAtom(ea[ik][1], symm, trans)
                t1 = t.tolist()
                it += len(t1)
                p1 += t1
        type.append(it)
    return (np.array(p1), type)

def ord(ea):
    order=raw_input("Pleas input the order of element:\nExample: C O Ca\n").split()
    if len(order) == 0:
        #print 'WARNING: '
        o1 = []
        for k in ea:
            o1.append(ea[k][0])
        o2 = set(o1)
        order = [item for item in o2]
    return order

def wPOSCAR(title, lat, type, pos):
    try:
        f = open('POSCAR', 'w')
    except:
        print 'ERROR: Cannot open file POSCAR'
        exit(0)
    f.write(title + "\n")
    f.write("1.0\n")
    for item in lat:
        f.write("%12.7f %12.7f %12.7f\n" % tuple(item))
    for item in type:
        f.write("%3d" % item)
    f.write("\n")
    f.write("Direct\n")
    for item in pos:
        f.write("%8.5f %8.5f %8.5f\n" % tuple(item))
        
if __name__ == '__main__':

    import sys
    args = sys.argv
    if len(args) == 1:
        print "usage: cif2pos.py ciffile [title]"
        exit(0)
    filename = args[1]
    if len(args) >=3:
        title = args[2]
    else:
        title = 'cif2pos.py'

    version()
    cif = readfile(filename)
    s = symmetry(cif)
    a = atominfo(cif)
    l =  lattice(cif)
    order = ord(a)
    (p, t) = p1atom(order, a, s[0], s[1])

    wPOSCAR(title, l, t, p)

    print '>'*14
    for item in order: 
        if len(item) == 1: 
            print item.upper(),
        else:
            iupp = item[0]
            print iupp.upper() + item[1],
    print
    print '>'*14
    print 'END'

#! /usr/bin/env python

'''
    USAGE:
        ./ingen.py in.conf ammonia.cif
'''
import sys
import os
import math
import shlex
import operator
import re
import random
import datetime
from subprocess import call
from elementdata import *

# keywords list and initial values
kw = {
'structure_file_type' : 'cif',
'project_name' : 'virtues_project',
'software' : 'castep',
'run_type' : 'geo_opt+phonon',
'supercell_dimension' : '1 1 1',
'partial_occupancy' : 'false',
'relax_cell' : 'false',
'enforce_symmetry' : 'true',
'electron_k_mesh' : '1 1 1',
'electron_k_mesh_offset' : '0 0 0',
'band_gap' : 'insulator',
'vdw_correction' : 'false',
'spin_polarized' : 'false',
'dft_u' : 'false',
'phonon_method' : 'dfpt',
'phonon_supercell' : '1 1 1',
'phonon_sc_el_k_mesh' : '1 1 1',
'phonon_k_mesh' : '1 1 1',
'phonon_k_mesh_offset' : '0 0 0',
'phonon_fine_k_mesh' : '1 1 1',
'phonon_fine_k_mesh_offset' : '0 0 0',
'potential_path' : '',
'nodes' : '8',
'threads': '1',
'wall_time' : '24',
'random_seed' : '100',
'wfc_grid' : '1 1 1'
}

# element information
el = ElementData()

class Cell:
    def __init__(self,a,b,c,alpha=None,beta=None,gamma=None):
        if alpha==None:
            self.lattice=[a,b,c]
        else:
            a_r=alpha/180.0*math.pi
            b_r=beta/180.0*math.pi
            g_r=gamma/180.0*math.pi
            self.lattice=[]
            self.lattice.append([a,0.0,0.0])
            self.lattice.append([b*math.cos(g_r),b*math.sin(g_r),0.0])
            c2=c*(math.cos(a_r)-math.cos(b_r)*math.cos(g_r))/math.sin(g_r)
            c3=c*(1.0-math.cos(a_r)**2-math.cos(b_r)**2-math.cos(g_r)**2+2*math.cos(a_r)*math.cos(b_r)*math.cos(g_r))**0.5/math.sin(g_r)
            self.lattice.append([c*math.cos(b_r),c2,c3])
        self.elem = None
        self.nelem = None

class Atom:
    def __init__(self, symbol, frac_xyz, occ=None):
        self.symbol = symbol
        self.frac_xyz = frac_xyz
        self.Z = el.elementnr[symbol]
        if occ==None:
            self.occ = 1.0
        else:
            self.occ = occ


def read_control(filename,kw):
    f = open(filename, 'r')
    full_text = f.read()
    f.close()
    chopped = full_text.split('\n')
    for i in range(len(chopped)):
        if '#' in chopped[i]:
            chopped[i]=chopped[i].split('#')[0]
        if (chopped[i].strip()=='') or (not ':' in chopped[i]):
            continue
        sp = chopped[i].strip().split(':')
        if len(sp)!=2 or sp[1]=='':
            print 'skipping line: ', chopped[i]
            continue
        key = sp[0].strip()
        value = sp[1].strip()
        if key in kw:
            kw[key]=value
        else:
            print 'invalid key: ', key
            sys.exit(1)

def read_vasp_poscar(filename):
    f = open(filename, 'r')

    for i in range(2):
        f.readline()     # discard the first three line

    line = f.readline()
    a = map(float, line.split()[:3])
    line = f.readline()
    b = map(float, line.split()[:3])
    line = f.readline()
    c = map(float, line.split()[:3])
    cell = Cell(a,b,c)

    line = f.readline()
    cell.elem = line.split()              # elements in unit cell

    if cell.elem[0].isdigit():
        print "POSCAR needs to be in the following format"
        print "Title"
        print "1.0"
        print "lattice vector 1"
        print "lattice vector 2"
        print "lattice vector 3"
        print "symbol for each element"
        print "number of atoms for each element"
        print "Direct"
        print "Atom 1 fractional coordinates"
        print "Atom 2 fractional coordinates"
        print "...."
        sys.exit()

    line = f.readline()
    cell.nelem = map(int, line.split())   # number of atoms for each element
    f.readline()

    na = sum(cell.nelem)
    atoms = []
    for i in range(len(cell.elem)):
        for j in range(cell.nelem[i]):
            line = f.readline()
            xyz = map(float, line.split()[:3])
            atoms.append(Atom(cell.elem[i],xyz))
    f.close()
    return cell, atoms


def read_castep_cell(filename):
    f = open(filename, 'r')
    full_text = f.read()
    f.close()

    aux = re.compile('%BLOCK LATTICE_CART(.*?)%ENDBLOCK LATTICE_CART',
                    re.DOTALL | re.I).search(full_text)
    chopped = aux.group(1).strip().split('\n')
    abc = []
    for i in [-3,-2,-1]:
        abc.append(map(float, chopped[i].strip().split()[:3]))
    print abc
    a=[abc[0][0],abc[1][0],abc[2][0]]
    b=[abc[0][1],abc[1][1],abc[2][1]]
    c=[abc[0][2],abc[1][2],abc[2][2]]
    cell = Cell(a,b,c)

    aux = re.compile('%BLOCK POSITIONS_FRAC(.*?)%ENDBLOCK POSITIONS_FRAC',
                     re.DOTALL | re.I).search(full_text)
    chopped = aux.group(1).strip().split('\n')
    atoms = []
    for i in range(len(chopped)):
        extra = chopped[i].strip().split()
        symbol = extra[0]
        xyz = map(float, extra[1:4])
        atoms.append(Atom(symbol,xyz))
    atoms.sort(key=operator.attrgetter('Z'))
    symbol = []
    for i in range(len(atoms)):
        symbol.append(atoms[i].symbol)
    seen = set()
    seen_add = seen.add 
    cell.elem = [x for x in symbol if not (x in seen or seen_add(x))]
    cell.nelem = []
    for i in range(len(cell.elem)):
        cell.nelem.append(symbol.count(cell.elem[i]))
    return cell, atoms


def read_cif(filename):
    f = open(filename, 'r')
    full_text = f.read()
    f.close()
    loop = 0
    sym_header = []
    sym_block = []
    atom_header = []
    atom_block = []
    reading_sym=0
    reading_atom=0
    full_text = full_text.replace('_space_group_symop_operation_xyz','_symmetry_equiv_pos_as_xyz')
    chopped = full_text.split('\n')
    for i in range(len(chopped)):
        chopped[i]=chopped[i].strip()
        if chopped[i].startswith('_cell_length_a'):
            a=float(chopped[i].split()[1].split('(')[0])
        if chopped[i].startswith('_cell_length_b'):
            b=float(chopped[i].split()[1].split('(')[0])
        if chopped[i].startswith('_cell_length_c'):
            c=float(chopped[i].split()[1].split('(')[0])
        if chopped[i].startswith('_cell_angle_alpha'):
            alpha=float(chopped[i].split()[1].split('(')[0])
        if chopped[i].startswith('_cell_angle_beta'):
            beta=float(chopped[i].split()[1].split('(')[0])
        if chopped[i].startswith('_cell_angle_gamma'):
            gamma=float(chopped[i].split()[1].split('(')[0])

        if reading_sym>0:
            if (not chopped[i].startswith('_') and ('x' in chopped[i] or 'y' in chopped[i] or 'z' in chopped[i])):
                sym_block.append(chopped[i].rstrip())
            elif chopped[i].startswith('_symmetry_equiv_pos'):
                sym_header.append(chopped[i].rstrip())
            else:
                reading_sym=0
            continue
        
        if reading_atom>0:
            if (not chopped[i].startswith('_') and len(chopped[i].split())==len(atom_header)):
                atom_block.append(chopped[i].split())
            elif (chopped[i].startswith('_atom_site_') and not chopped[i].startswith('_atom_site_aniso')):
                atom_header.append(chopped[i].rstrip())
            else:
                reading_atom=0
            continue

        if (chopped[i].startswith('_symmetry_equiv_pos')):
            sym_header.append(chopped[i].rstrip())
            reading_sym += 1
            continue
        if (chopped[i].startswith('_atom_site_') and not chopped[i].startswith('_atom_site_aniso')):
            atom_header.append(chopped[i].rstrip())
            reading_atom += 1
            continue

    cell = Cell(a,b,c,alpha,beta,gamma)
    atoms = []

    isym = sym_header.index('_symmetry_equiv_pos_as_xyz')
    it = atom_header.index('_atom_site_label')
    ix = atom_header.index('_atom_site_fract_x')
    iy = atom_header.index('_atom_site_fract_y')
    iz = atom_header.index('_atom_site_fract_z')
    io = atom_header.index('_atom_site_occupancy')
    for i in range(len(atom_block)):
        symbol=atom_block[i][it].rstrip('0123456789+-')
        x=float(atom_block[i][ix].split('(')[0])
        y=float(atom_block[i][iy].split('(')[0])
        z=float(atom_block[i][iz].split('(')[0])
        x = x-math.floor(x)
        y = y-math.floor(y)
        z = z-math.floor(z)
        occ=float(atom_block[i][io].split('(')[0])
        atoms.append(Atom(symbol,[x,y,z],occ))
        for j in range(len(sym_block)):
            new_xyz = shlex.split(sym_block[j])[isym].strip('\'').split(',')
            newx = eval(new_xyz[0].replace('1/','1.0/'))
            newy = eval(new_xyz[1].replace('1/','1.0/'))
            newz = eval(new_xyz[2].replace('1/','1.0/'))
            newx = newx-math.floor(newx)
            newy = newy-math.floor(newy)
            newz = newz-math.floor(newz)
            rmin = 10000.0
            for k in range(len(atoms)):
                r = (newx-atoms[k].frac_xyz[0])**2+(newy-atoms[k].frac_xyz[1])**2+(newz-atoms[k].frac_xyz[2])**2
                if r<rmin:
                    rmin =r
            if rmin > 0.0001:
                symbol=atom_block[i][it].rstrip('0123456789+-')
                atoms.append(Atom(symbol,[newx,newy,newz],occ))

    atoms.sort(key=operator.attrgetter('Z'))
    symbol = []
    for i in range(len(atoms)):
        symbol.append(atoms[i].symbol)
    seen = set()
    seen_add = seen.add 
    cell.elem = [x for x in symbol if not (x in seen or seen_add(x))]
    cell.nelem = []
    for i in range(len(cell.elem)):
        cell.nelem.append(symbol.count(cell.elem[i]))
    return cell,atoms


def write_vasp_incar(filename,kw,cell,step):
    f = open(filename, 'w')
    print >> f, 'PREC   =  accurate'   
    print >> f, 'ISTART =      0'
    print >> f, 'ICHARG =      2'   
    if kw['spin_polarized']=='true':
        print >> f, 'ISPIN  =      2'  
        print >> f, 'MAGMOM =   '+' '.join(str(ne)+'*0.1' for ne in cell.nelem)
    else:
        print >> f, 'ISPIN  =      1'  
    if kw['enforce_symmetry']=='true':
        print >> f, '!ISYM   =      0'
    else:
        print >> f, 'ISYM   =      0'
    cutoff=[]
    for i in range(len(cell.elem)):
        cutoff.append(el.vasp_cutoff[cell.elem[i]])
    print >> f, 'ENCUT  = '+str(max(cutoff)*2.0)
    print >> f, 'NELM   =     1000  '
    print >> f, 'EDIFF  =   1.0e-8  '
    print >> f, 'LREAL  =   .FALSE. ' 
    print >> f, 'ALGO   =   normal  '
    print >> f, 'ADDGRID = .TRUE.'
    print >> f, 'ISMEAR =     0   '
    print >> f, 'SIGMA  =   0.05  '
    if kw['vdw_correction']=='true':
        print >> f, 'LUSE_VDW = .TRUE.'
        print >> f, 'AGGAC = 0.0000'
        print >> f, 'GGA = MK'
        print >> f, 'PARAM1 = 0.1234'
        print >> f, 'PARAM2 = 1.0000'
    if kw['dft_u']=='true':
        print >> f, 'LDAU   =  .TRUE.'
        print >> f, 'LDAUTYPE = 2'
        print >> f, 'LDAUL  =   -1 -1 -1 2'
        print >> f, 'LDAUU  =   0  0  0  5.0'
        print >> f, 'LDAUJ  =   0  0  0  0'
        print >> f, 'LDAUPRINT = 0'
        print >> f, 'LASPH  =  .TRUE.'
    if kw['run_type']=='geo_opt' or \
       ('phonon' in kw['run_type'] and step==0) or \
       ('ir' in kw['run_type'] and step==0):
        print >> f, 'EDIFFG =   1.0e-7   '
        print >> f, 'NSW    =   1000  '
        print >> f, 'IBRION =   2   '
        print >> f, 'POTIM  =   0.5  '
        print >> f, 'ISIF   =  2'
    elif ('phonon' in kw['run_type'] and step==1) or \
       ('ir' in kw['run_type'] and step==1):
        print >> f, '!EDIFFG =   1.0e-7   '
        print >> f, 'NSW    =   1  '
        print >> f, 'IBRION =   8   '
        print >> f, '!POTIM  =   0.5  '
        print >> f, '!ISIF   =  2'
    elif kw['run_type']=='md':
        print >> f, '!EDIFFG =   1.0e-7   '
        print >> f, 'NSW    =   1000  '
        print >> f, 'IBRION =   0   '
        print >> f, 'POTIM  =   1.0  '
        print >> f, '!ISIF   =  2'
        print >> f, 'TEBEG  =  300.0'
        print >> f, 'TEEND  =  300.0 '  
        print >> f, 'SMASS  =     -1 '
    print >> f, 'LWAVE = .FALSE.'
    print >> f, 'LCHARG = .FALSE.'
    if ('ir' in kw['run_type'] and step==1):
        print >> f, 'LEPSILON = .TRUE.'
    if step==1:
        print >> f, '!NPAR   =      8  ' 
    else:
        print >> f, 'NPAR   =      8  ' 
    print >> f, 'LPLANE =  .FALSE.'
    print >> f, 'LSCALU = .FALSE.'
    print >> f, 'LSCALAPACK = .FALSE.'
    f.close()


def write_vasp_poscar(filename,kw,cell,atoms):
    sc = map(int,kw['supercell_dimension'].strip().split())
    random.seed(float(kw['random_seed'].strip()))
    nelem = [x*sc[0]*sc[1]*sc[2] for x in cell.nelem]
    f = open(filename, 'w')
    print >> f, kw['project_name']
    print >> f, '1.0'
    print >> f, '%21.16f' % (sc[0]*cell.lattice[0][0]),'%21.16f' % (sc[0]*cell.lattice[0][1]),'%21.16f' % (sc[0]*cell.lattice[0][2])
    print >> f, '%21.16f' % (sc[1]*cell.lattice[1][0]),'%21.16f' % (sc[1]*cell.lattice[1][1]),'%21.16f' % (sc[1]*cell.lattice[1][2])
    print >> f, '%21.16f' % (sc[2]*cell.lattice[2][0]),'%21.16f' % (sc[2]*cell.lattice[2][1]),'%21.16f' % (sc[2]*cell.lattice[2][2])
    print >> f, ' '.join(cell.elem)
    print >> f, ' '.join(str(ne*sc[0]*sc[1]*sc[2]) for ne in cell.nelem)
    print >> f, 'Direct'
    for j in range(len(atoms)):
        for s0 in range(sc[0]):
            for s1 in range(sc[1]):
                for s2 in range(sc[2]):
                    if (random.random()<=atoms[j].occ):
                        x = (atoms[j].frac_xyz[0]+s0)/sc[0]
                        y = (atoms[j].frac_xyz[1]+s0)/sc[1]
                        z = (atoms[j].frac_xyz[2]+s0)/sc[2]
                        print >> f, '%21.16f' % x,'%21.16f' % y,'%21.16f' % z, '%4s' % '!'+atoms[j].symbol
                    else:
                        nelem[cell.elem.index(atoms[j].symbol)] -= 1
    print cell.elem
    print cell.nelem
    print nelem
    f.close()


def write_vasp_kpoints(filename,kw):
    f = open(filename, 'w')
    print >> f, 'Automatic mesh'
    print >> f, '0'
    print >> f, 'Monkhorst-Pack'
    print >> f, kw['electron_k_mesh']
    print >> f, kw['electron_k_mesh_offset']
    f.close()

def write_vasp_potcar(filename,kw,el,cell):
    fout = open(filename, 'w')
    for i in range(len(cell.elem)):
        fin = open(os.path.join(kw['potential_path'],el.vasp_pot[cell.elem[i]],'POTCAR'), 'r')
        full_text = fin.read()
        fin.close()
        fout.write(full_text)
    fout.close()


def write_pbs(filename,kw):
    f = open(filename, 'w')
    print >> f, '#!/bin/bash'
    print >> f, '#PBS -q batch'
    print >> f, '#PBS -V'
    print >> f, '#PBS -l walltime='+kw['wall_time']+':00:00'
    print >> f, '#PBS -l nodes='+kw['nodes']+':ppn=32'
    print >> f, '#PBS -N '+kw['project_name']
    print >> f, '#PBS -j oe'
    print >> f, ' '
    if kw['software']=='vasp':
        print >> f, 'VASP=/software/user_tools/current/cades-virtues/apps/vasp/intel/5.4.1/cades_opt/vasp_std'
        print >> f, 'cd $PBS_O_WORKDIR'
        print >> f, ' '
        print >> f, 'mpirun -np ',int(kw['nodes'])*32,' $VASP_MPI_FLAGS $VASP'
    elif kw['software']=='castep':
        print >> f, 'JOBSEED='+kw['project_name']
        print >> f, 'JOBDOS=${JOBSEED}_PhonDOS'
        print >> f, 'cd $PBS_O_WORKDIR'
        print >> f, ' '
        print >> f, 'mpirun -np ',int(kw['nodes'])*32,' $CASTEP_MPI_FLAGS castep.mpi $JOBSEED'
        print >> f, 'cp ${JOBSEED}.check ${JOBDOS}.check'
        print >> f, 'mpirun -np ',int(kw['nodes'])*32,' $CASTEP_MPI_FLAGS castep.mpi $JOBDOS'
    f.close()


def write_phonopy_script(filename,kw):
    f = open(filename, 'w')
    print >> f, 'phonopy -d --dim=\"'+kw['phonon_supercell']+'\" -c POSCAR-unitcell'
    print >> f, 'mv SPOSCAR POSCAR'
    print >> f, 'rm POSCAR-???'
    print >> f, 'rm disp.yaml'
    print >> f, '#phonopy --fc vasprun.xml'
    print >> f, '#phonopy -c POSCAR-unitcell mesh.conf'
    print >> f, '#2climax.py -v POSCAR-unitcell mesh.yaml'
    f.close()

def write_phonopy_conf(filename,kw,cell):
    f = open(filename, 'w')
    print >> f, 'ATOM_NAME = '+' '.join(cell.elem)
    print >> f, 'DIM = '+kw['phonon_supercell']
    print >> f, 'FORCE_CONSTANTS = read'
    print >> f, 'MP = '+kw['phonon_fine_k_mesh']
    print >> f, 'GAMMA_CENTER = .TRUE.'
    print >> f, 'EIGENVECTORS = .TRUE.'
    f.close()

def init_rmg(proj_path):
    #from shutill import copy
    init_dir = os.path.join(proj_path, 'init')
    relax_dir = os.path.join(proj_path, 'relax')
    unitcell_dir = os.path.join(proj_path, 'unitcell')
    phonon_dir = os.path.join(proj_path, 'phonon')

    for tmp_dir in [init_dir, relax_dir, unitcell_dir, phonon_dir]:
        if not os.path.isdir(tmp_dir):
            os.mkdir(tmp_dir)

    #copy('*cif')
    os.system('cp *cif *conf %s'% init_dir)

    # generate relaxed unitcell
    #from interface.rmg import get_relaxed_unitcell
    #get_relaxed_unitcell()

    f = open(os.path.join(unitcell_dir, 'unitcell.sh'), 'wb')
    print >> f, '#! /bin/bash'
    print >> f, 'cp ../relax/rmg.in ../relax/rmg.in.00.log .'
    print >> f, '#python ~/bin/generate_unitcell_after_relaxation.py'
    f.close()
    os.system('chmod a+x %s'%(os.path.join(unitcell_dir, 'unitcell.sh')))

def write_rmg_inp(proj_path, filename, kw, el, cell, atoms, step):
    sc = map(int, kw['supercell_dimension'].strip().split())
    nelem = [x*sc[0]*sc[1]*sc[2] for x in cell.nelem]
    f = open(os.path.join(proj_path, 'relax', filename), 'wb')
    print >> f, 'description="%(project_name)s"'% kw
    print >> f, 'start_mode="LCAO Start"'
    print >> f, '#start_mode="Restart From File"'
    print >> f, 'wavefunction_grid="%(wfc_grid)s"'% kw
    print >> f, 'kpoint_mesh="%(electron_k_mesh)s"'% kw
    if kw['enforce_symmetry']=='true':
        print >> f, 'use_symmetry="true"'
    if kw['run_type']=='geo_opt' or ('phonon' in kw['run_type'] and step==0):
        print >> f, 'calculation_mode="Relax Structure"'
        print >> f, 'max_md_steps="300"'
        print >> f, 'max_scf_steps="300"'
        print >> f, 'relax_max_force="1.0e-4"'
        print >> f, 'rms_convergence_criterion="1.0e-8"'
    if kw['band_gap'] == 'insulator':
        print >> f, 'occupation_type="Fixed"'
    elif kw['band_gap'] == 'metal':
        print >> f, 'occupation_type="Fermi Dirac"'
    print >> f, 'subdiag_driver="scalapack"'
    print >> f, 'charge_mixing_type="Pulay"'
    print >> f, 'charge_pulay_order="3"'
    print >> f, 'charge_pulay_scale="0.5"'
    print >> f, 'bravais_lattice_type="Orthorhombic Primitive"'
    print >> f, 'crds_units="Angstrom"'
    print >> f, 'a_length="%f"'% (sc[0]*cell.lattice[0][0])
    print >> f, 'b_length="%f"'% (sc[1]*cell.lattice[1][1])
    print >> f, 'c_length="%f"'% (sc[2]*cell.lattice[2][2])
    print >> f, 'atomic_coordinate_type="Cell Relative"'
    print >> f, 'atoms="'
    for i in range(len(atoms)):
        for s0 in range(sc[0]):
            for s1 in range(sc[1]):
                for s2 in range(sc[2]):
                    if random.random() <= atoms[i].occ:
                        x = (atoms[i].frac_xyz[0]+s0)/sc[0]
                        y = (atoms[i].frac_xyz[1]+s0)/sc[1]
                        z = (atoms[i].frac_xyz[2]+s0)/sc[2]
                        print >> f, '%2s%15.9f%15.9f%15.9f%3d'%(
                                    atoms[i].symbol, x, y, z, 1)
                    else:
                        nelem[cell.elem.index(atoms[i].symbol)] -= 1
    print >> f, '"'
    f.close()

def write_rmg_pbs(proj_path, filename, kw):
    home_path = os.path.expanduser('~')
    f = open(os.path.join(proj_path, 'relax', filename), 'wb')
    print >> f, '# mandatory'
    print >> f, 'NODES       = %(nodes)-s'% kw
    print >> f, 'TIME        = %(wall_time)-s'% kw
    print >> f, '%-12s= %-s'%('EXEINPUT', 'rmg.in')
    print >> f, '%-12s= %-s/bin/rmg-cpu'%('EXEPATH', home_path)
    print >> f, 'THREADS     = %(threads)-s'% kw
    print >> f, ''
    print >> f, '# optional'
    print >> f, 'NAME        = %(project_name)-s'% kw
    print >> f, '%-12s= %-s'%('IS_SUBMIT', 'true')
    print >> f, '%-12s= %-s'%('QUEUE', 'none')
    f.close()

def write_rmg_phonopy(proj_path, filename, kw, cell):
    f = open(os.path.join(proj_path, 'phonon', filename), 'wb')
    print >> f, '# build supercells'
    print >> f, 'phonopy --rmg -d -dim=\"%(phonon_supercell)s\" -c unitcell.in'% kw
    print >> f, '# calculate force sets'
    print >> f, '#phonopy --rmg -f supercells/supercell-*/*in.00.log'
    print >> f, '# plot band+dos'
    print >> f, '#phonopy --rmg -c unitcell.in -s -p band-dos.conf'
    print >> f, '# plot band only'
    print >> f, '#phonopy --rmg -c unitcell.in -s -p band.conf'
    print >> f, '# plot dos only; also needs dos.conf file'
    print >> f, '#phonopy --rmg -c unitcell.in -s -p mesh.conf'
    f.close()
    os.system('chmod a+x %s'%(os.path.join(proj_path, 'phonon', filename)))

    f = open(os.path.join(proj_path, 'phonon', 'band.conf'), 'wb')
    print >> f, 'DIM = %(phonon_supercell)s'% kw
    print >> f, 'PRIMITIVE_AXIS = 1.0 0.0 0.0  0.0 1.0 0.0  0.0 0.0 1.0'
    print >> f, 'BAND = 0.0 0.0 0.0  0.0 0.5 0.0  0.5 0.5 0.0  0.5 0.5 0.5'
    print >> f, 'BAND_LABELS = \Gamma X M R'
    f.close()

    f = open(os.path.join(proj_path, 'phonon', 'dos.conf'), 'wb')
    print >> f, 'DIM = %(phonon_supercell)s'% kw
    print >> f, 'DOS = .TRUE.'
    print >> f, 'DOS_RANGE = 0 40 0.02'
    f.close()

    f = open(os.path.join(proj_path, 'phonon', 'mesh.conf'), 'wb')
    print >> f, 'DIM = %(phonon_supercell)s'% kw
    print >> f, 'ATOM_NAME = '+' '.join(cell.elem)
    print >> f, 'MP = %(phonon_fine_k_mesh)s'% kw
    print >> f, 'GAMMA_CENTER = .TRUE.'
    print >> f, 'EIGENVECTORS= .TRUE.'
    f.close()

def write_castep_cell(filename,kw,el,cell,atoms,step):
    sc = map(int,kw['supercell_dimension'].strip().split())
    random.seed(float(kw['random_seed'].strip()))
    nelem = [x*sc[0]*sc[1]*sc[2] for x in cell.nelem]
    f = open(filename, 'w')
    print >> f, '%BLOCK LATTICE_CART'
    print >> f, '%21.16f' % (sc[0]*cell.lattice[0][0]),'%21.16f' % (sc[1]*cell.lattice[1][0]),'%21.16f' % (sc[2]*cell.lattice[2][0])
    print >> f, '%21.16f' % (sc[0]*cell.lattice[0][1]),'%21.16f' % (sc[1]*cell.lattice[1][1]),'%21.16f' % (sc[2]*cell.lattice[2][1])
    print >> f, '%21.16f' % (sc[0]*cell.lattice[0][2]),'%21.16f' % (sc[1]*cell.lattice[1][2]),'%21.16f' % (sc[2]*cell.lattice[2][2])
    print >> f, '%ENDBLOCK LATTICE_CART'
    print >> f, ' '
    print >> f, '%BLOCK POSITIONS_FRAC'
    for j in range(len(atoms)):
        for s0 in range(sc[0]):
            for s1 in range(sc[1]):
                for s2 in range(sc[2]):
                    if (random.random()<=atoms[j].occ):
                        x = (atoms[j].frac_xyz[0]+s0)/sc[0]
                        y = (atoms[j].frac_xyz[1]+s0)/sc[1]
                        z = (atoms[j].frac_xyz[2]+s0)/sc[2]
                        print >> f, '%4s' % atoms[j].symbol, '%21.16f' % x,'%21.16f' % y,'%21.16f' % z
                    else:
                        nelem[cell.elem.index(atoms[j].symbol)] -= 1
    print >> f, '%ENDBLOCK POSITIONS_FRAC'
    print >> f, ' '

    if ('phonon' in kw['run_type'] and step==1) or \
       ('ir' in kw['run_type'] and step==1):
        print >> f, 'PHONON_FINE_KPOINT_MP_GRID : '+kw['phonon_fine_k_mesh']
        print >> f, 'PHONON_FINE_KPOINT_MP_OFFSET :'+kw['phonon_fine_k_mesh_offset']
        if kw['phonon_method']=='dfpt':
            print >> f, 'PHONON_KPOINT_MP_GRID : '+kw['phonon_k_mesh']
            print >> f, 'PHONON_KPOINT_MP_OFFSET : '+kw['phonon_k_mesh_offset']
        else:
            sc = kw['phonon_supercell'].split()
            print >> f, '%BLOCK PHONON_SUPERCELL_MATRIX'
            print >> f, '     '+sc[0]+'     0     0'
            print >> f, '     0     '+sc[1]+'     0'
            print >> f, '     0     0     '+sc[2]
            print >> f, '%ENDBLOCK PHONON_SUPERCELL_MATRIX'
            print >> f, 'SUPERCELL_KPOINT_MP_GRID : '+kw['phonon_sc_el_k_mesh']

    print >> f, 'KPOINT_MP_GRID : '+kw['electron_k_mesh']
    print >> f, 'KPOINT_MP_OFFSET : '+kw['electron_k_mesh_offset']
    if kw['enforce_symmetry']=='true':
        print >> f, 'SYMMETRY_GENERATE'
        print >> f, 'SNAP_TO_SYMMETRY'
    print >> f, ' '
    if kw['relax_cell']=='true':
        print >> f, '%BLOCK EXTERNAL_PRESSURE'
        print >> f, '    0.0000000000    0.0000000000    0.0000000000'
        print >> f, '                    0.0000000000    0.0000000000'
        print >> f, '                                    0.0000000000'
        print >> f, '%ENDBLOCK EXTERNAL_PRESSURE'
    else:
        print >> f, 'FIX_ALL_CELL : true'
    print >> f, 'FIX_COM : false'
    print >> f, ' '
    print >> f, '%BLOCK SPECIES_MASS'
    for i in range(len(cell.elem)):
        print >> f, cell.elem[i], el.elementweight[cell.elem[i]]
    print >> f, '%ENDBLOCK SPECIES_MASS'
    print >> f, ' '
    print >> f, '%BLOCK SPECIES_POT'
    for i in range(len(cell.elem)):
        if kw['phonon_method']=='dfpt':
            print >> f, cell.elem[i], el.castep_recpot[cell.elem[i]]
        else:
            print >> f, cell.elem[i], el.castep_usp[cell.elem[i]]
    print >> f, '%ENDBLOCK SPECIES_POT'
    print cell.elem
    print cell.nelem
    print nelem
    f.close()


def write_castep_param(filename,kw,step):
    f = open(filename, 'w')

    if kw['run_type']=='geo_opt' or \
       ('phonon' in kw['run_type'] and step==0) or \
       ('ir' in kw['run_type'] and step==0):
        print >> f, 'task : GeometryOptimization'
    elif ('phonon' in kw['run_type'] and step==1) or \
         ('ir' in kw['run_type'] and step==1):
        print >> f, 'task : Phonon'
        print >> f, 'continuation : default'
    print >> f, 'opt_strategy : speed'
    print >> f, 'page_wvfns :   0'
    print >> f, 'calculate_stress : true'
    print >> f, 'popn_calculate : false'
    print >> f, 'num_dump_cycles : 0'
    print >> f, 'xc_functional : PBE'
    if kw['spin_polarized']=='true':
        print >> f, 'spin_polarized : true'
    else:
        print >> f, 'spin_polarized : false'

    cutoff=[]
    for i in range(len(cell.elem)):
        if kw['phonon_method']=='dfpt':
            cutoff.append(el.castep_recpot_cutoff[cell.elem[i]])
        else:
            cutoff.append(el.castep_usp_cutoff[cell.elem[i]])
    print >> f, 'cut_off_energy : '+str((int(max(cutoff)*1.1/10)+1)*10)

    if kw['run_type']=='geo_opt' or \
       ('phonon' in kw['run_type'] and step==0) or \
       ('ir' in kw['run_type'] and step==0):
        print >> f, 'grid_scale :        2.0'
        print >> f, 'fine_grid_scale :   3.0'
        print >> f, 'elec_energy_tol :   5.0e-010'
        print >> f, 'max_scf_cycles :     1000'
        if kw['band_gap']=='insulator':
            print >> f, 'fix_occupancy : true'
        else:
            print >> f, 'fix_occupancy : false'
            print >> f, 'smearing_width : 0.1 eV'
        print >> f, 'metals_method : dm'
        print >> f, 'mixing_scheme : Pulay'
        print >> f, 'mix_charge_amp :  0.5'
        print >> f, 'mix_charge_gmax : 1.5'
        print >> f, 'mix_history_length : 20'
        print >> f, 'geom_energy_tol :  5.0e-009'
        print >> f, 'geom_force_tol :   1.0e-003'
        print >> f, 'geom_disp_tol :   5.0e-004'
        print >> f, 'geom_max_iter :     1000'
        print >> f, 'geom_method : BFGS'
        if kw['relax_cell']=='true':
            print >> f, 'finite_basis_corr :   2'
            print >> f, 'finite_basis_npoints :  3'
            print >> f, 'geom_modulus_est :   100.0 GPa'
            print >> f, 'geom_stress_tol :  0.002'

    elif ('phonon' in kw['run_type'] and step==1) or \
         ('ir' in kw['run_type'] and step==1):
        if kw['phonon_method']=='dfpt':
            print >> f, 'phonon_fine_method : interpolate'
            print >> f, 'phonon_calc_lo_to_splitting : true'
            print >> f, 'born_charge_sum_rule : true'
            print >> f, 'phonon_max_cycles : 500'
            print >> f, 'efield_max_cycles : 500'
            print >> f, 'bs_max_iter : 250'
            print >> f, 'bs_max_cg_steps : 25'
        else:
            print >> f, 'phonon_method : finitedisplacement'
            print >> f, 'phonon_fine_method : supercell'
            print >> f, 'phonon_calc_lo_to_splitting : false'
            print >> f, 'born_charge_sum_rule : false'
        print >> f, 'phonon_sum_rule : true'
        print >> f, 'backup_interval : 900'
        print >> f, 'bs_write_eigenvalues : false'

    f.close()


######################################################
# main program
######################################################

# read control file
read_control(sys.argv[1],kw)

if kw['structure_file_type']=='cif':
    # read and parse cif file
    [cell,atoms] = read_cif(sys.argv[2])
elif kw['structure_file_type']=='vasp':
    # parse POSCAR file
    [cell,atoms] = read_vasp_poscar(sys.argv[2])
elif kw['structure_file_type']=='cell':
    # parse cell file
    [cell,atoms] = read_castep_cell(sys.argv[2])

# creae folder for project
if not os.path.exists(kw['project_name']):
    proj_path = kw['project_name']
else:
    proj_path = kw['project_name']+'-'+datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
os.makedirs(proj_path)

# generate vasp calculation
if kw['software']=='vasp':
    # generate POSCAR file
    write_vasp_poscar(os.path.join(proj_path,'POSCAR'),kw,cell,atoms)

    # generate KPOINTS file
    write_vasp_kpoints(os.path.join(proj_path,'KPOINTS'),kw)

    # generate INCAR file
    write_vasp_incar(os.path.join(proj_path,'INCAR'),kw,cell,0)

    # generate POTCAR file
    write_vasp_potcar(os.path.join(proj_path,'POTCAR'),kw,el,cell)

    # generate pbs file
    write_pbs(os.path.join(proj_path,'virtues.pbs'),kw)

    # copy vdw_kernel file for VASP calculation with vdw corrections
    if kw['vdw_correction']=='true':
        call(['cp', '/home/yyc/bin/vdw_kernel.bindat', proj_path])

    if 'phonon' in kw['run_type'] or 'ir' in kw['run_type']:
        sub_path = os.path.join(proj_path, 'phonon')
        os.makedirs(sub_path)
        # generate INCAR file
        write_vasp_incar(os.path.join(sub_path,'INCAR'),kw,cell,1)

        write_phonopy_script(os.path.join(sub_path,'vasp-phonopy.sh'),kw)
        write_phonopy_conf(os.path.join(sub_path,'mesh.conf'),kw,cell)

        call(['cp', os.path.join(proj_path,'POTCAR'), sub_path])
        call(['cp', os.path.join(proj_path,'KPOINTS'), sub_path])
        call(['cp', os.path.join(proj_path,'virtues.pbs'), sub_path])
        if kw['vdw_correction']=='true':
            call(['cp', '/home/yyc/bin/vdw_kernel.bindat', sub_path])

# generate castep calculation
elif kw['software']=='castep':
    # generate .cell file
    write_castep_cell(os.path.join(proj_path, kw['project_name']+'.cell'),kw,el,cell,atoms,0)

    # generate .param file
    write_castep_param(os.path.join(proj_path, kw['project_name']+'.param'),kw,0)

    # generate PhonDOS.cell file
    write_castep_cell(os.path.join(proj_path, kw['project_name']+'_PhonDOS.cell'),kw,el,cell,atoms,1)

    # generate PhonDOS.param file
    write_castep_param(os.path.join(proj_path, kw['project_name']+'_PhonDOS.param'),kw,1)

    # generate pbs file
    write_pbs(os.path.join(proj_path,'virtues.pbs'),kw)

elif kw['software'] == 'rmg':
    # initilization
    init_rmg(proj_path)

    # generate rmg.in file
    write_rmg_inp(proj_path, 'rmg.in', kw, el, cell, atoms, 0)

    # generate pbs configuration file
    write_rmg_pbs(proj_path, 'pbs.conf', kw)

    # generate phonopy files
    write_rmg_phonopy(proj_path, 'phonon.sh', kw, cell)

elif kw['software'] == 'qe':
    # initilization
    init_qe(proj_path, kw)

    # generate qe.in file
    write_qe_in(proj_path, 'qe.in', kw, el, cell, atoms, 0)

    # generate pbs configuration file
    write_qe_pbs(proj_path, 'pbs.conf', kw)

    # generate phonopy files
    write_qe_phonopy(proj_path, 'phonon.sh', kw, cell)

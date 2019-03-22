#! /usr/bin/env python

import sys, os, re

file_elements = os.path.dirname(os.path.realpath(__file__)) + "/elements.txt"
f = open(file_elements, 'r')

table = []
atnum = []
sym = []
for line in f:
    aux = line.split()
    if(aux[0].startswith('#') or len(aux)!=6):
        continue
    table.append(aux)
    atnum.append(int(aux[0]))
    sym.append(aux[1])
f.close()

# Information for each atom in the system
class Atom:
    def __init__(self, eid, pos, frc=None):
        if isinstance(eid,int):
            i = atnum.index(eid)
        else:
            i = sym.index(eid)
        self.Z = int(table[i][0])            # atomic number
        self.symbol = table[i][1]            # element symbol
        self.mass = float(table[i][2])       # atomic mass, in amu
        self.xc_tot = float(table[i][3])     # neutron scattering total cross-section
        self.xc_inc = float(table[i][4])     # neutron scattering incoherent cross-section
        self.b_coh = float(table[i][5])      # neutron scattering coheren length
        self.pos = pos                       # atomic coordinates
        if frc==None:
            self.frc = [0.0,0.0,0.0]
        else:
            self.frc = frc

def unix2dos(file_climax):
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# replace \n with \r\n in the aclimax/oclimax file
#
    f = open(file_climax, 'r')
    full_text = f.read()
    f.close()
    f = open(file_climax, 'w')
    f.write(full_text.replace("\n", "\r\n"))
    f.close()
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def renorm(dxyz,atoms):
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Produces the mass weighted normal modes eigenvectors (normalised)
#
    for i in range(len(dxyz)):
    # iteration through frequency
        aux = 0.0
        for j in range(len(dxyz[0])):
        # Iteration through atoms
            for k in range(0,len(dxyz[0][0])):
                aux = aux + dxyz[i][j][k]**2*atoms[j].mass
        if aux==0.0:
            continue
        for j in range(len(dxyz[0])):
        # Iteration through atoms
            for k in range(len(dxyz[0][0])):
                dxyz[i][j][k] = dxyz[i][j][k]*(atoms[j].mass/aux)**0.5
    return dxyz



def get_poscar(file_poscar):
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Input: VASP POSCAR of the unit cell
# Output: lists of symbols and coordinates
#
    f = open(file_poscar, 'r')
    
    f.readline()     # discard the first line
    line = f.readline()
    scale = float(line.split()[0])
    
    cell = [[0 for _ in range(3)] for _ in range(3)]
    for i in range(3):
        line = f.readline()
        cell[i] = map(float, line.split()[:3])
    
    line = f.readline()
    elem = line.split()              # elements in unit cell

    if elem[0].isdigit():
        print "POSCAR needs to be in the following format"
        print "Title"
        print "x.x"
        print "lattice vector 1"
        print "lattice vector 2"
        print "lattice vector 3"
        print "symbol for each element"
        print "number of atoms for each element"
        print "Direct"
        print "Atom 1 coordinates" 
        print "Atom 2 coordinates"
        print "...."
        sys.exit()
    
    line = f.readline()
    nelem = map(int, line.split())   # number of atoms for each element
    f.readline()
    
    na = sum(nelem)
    symbol = []
    for i in range(len(elem)):
    	for j in range(nelem[i]):
    		symbol.append(elem[i])        # symbol list

    atoms = []
    for i in range(na):
    	line = f.readline()
    	xyz = map(float, line.split()[:3])     # fractional coordinates
        sx = xyz[0]*cell[0][0]+xyz[1]*cell[1][0]+xyz[2]*cell[2][0]
        sy = xyz[0]*cell[0][1]+xyz[1]*cell[1][1]+xyz[2]*cell[2][1]
        sz = xyz[0]*cell[0][2]+xyz[1]*cell[1][2]+xyz[2]*cell[2][2]
        sxyz = [scale*sx, scale*sy, scale*sz]     # absolute xyz
        atom = Atom(symbol[i],sxyz,xyz)
        atoms.append(atom)
    f.close()

    return atoms, cell    
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


def get_phonopy(file_phonopy):
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Input: mesh.yaml from phonopy (VASP force constants) 
#        old phonopy format without atomic coordinates
# Output: phonon frequencies and modes
#
    f = open(file_phonopy, 'r')

    while True:    
        line = f.readline()
        if line.split(':')[0]=='mesh':
            break
    qmesh = map(int, re.findall(r"[-+]?\d*\.\d+|\d+", line))
    qtot = 1
    for i in qmesh:
        qtot = qtot*i             # number of total q points in BZ

    while True:    
        line = f.readline()                               
        if line.split(':')[0]=='nqpoint':
            break
    nq = int(line.split()[1])     # number of irreducible q points

    while True:    
        line = f.readline()                               
        if line.split(':')[0]=='natom':
            break
    na = int(line.split()[1])     # number of atoms
    nb = na*3                     # number of bands at each q point

    while True:    
        line = f.readline()                               
        if line.split(':')[0]=='phonon':
            break

    qw = [[0 for i in range(4)] for i in range(nq)]
    freq = [[0 for i in range(nb)] for i in range(nq)]
    mode = [[[[[0 for i in range(2)] for i in range(3)]
           for i in range(na)] for i in range(nb)] for i in range(nq)]
    dxyz = [[[[0 for i in range(6)]
           for i in range(na)] for i in range(nb)] for i in range(nq)]
    for iq in range(nq):
        line = f.readline()
        qw[iq][0:3] = map(float,re.findall(r"[-+]?\d*\.\d+|\d+", line))
        line = f.readline()
        qw[iq][3] = float(line.split()[1])/float(qtot)
        f.readline()
        for ib in range(nb):
            f.readline()
            line = f.readline()
            freq[iq][ib] = float(line.split()[1])
            freq[iq][ib] *= 33.3564  # convert from THz to cm-1
            f.readline()
            for ia in range(na):
                f.readline()
                for i in range(3):
                    line=f.readline()
                    mode[iq][ib][ia][i] = map(float,
                        re.findall(r"[-+]?\d*\.\d+|\d+", line))
                xyz = []
                for i in range(3):
                    for j in range(2):
                        xyz.append(mode[iq][ib][ia][i][j])
                for i in range(6):
                    dxyz[iq][ib][ia][i] = xyz[i]*qw[iq][3]**0.5
        f.readline()

    f.close()

    return nq, qw, nb, freq, dxyz
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def get_mesh_yaml(file_mesh_yaml):
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Input: mesh.yaml from phonopy (new format containing atomic coordinates) 
# Output: atomic coordinates and phonon information
#
    f = open(file_mesh_yaml, 'r')

    while True:    
        line = f.readline()
        if line.split(':')[0]=='mesh':
            break
    qmesh = map(int, re.findall(r"[-+]?\d*\.\d+|\d+", line))
    qtot = 1
    for i in qmesh:
        qtot = qtot*i             # number of total q points in BZ

    while True:    
        line = f.readline()                               
        if line.split(':')[0]=='nqpoint':
            break
    nq = int(line.split()[1])     # number of irreducible q points

    while True:    
        line = f.readline()                               
        if line.split(':')[0]=='natom':
            break
    na = int(line.split()[1])     # number of atoms
    nb = na*3                     # number of bands at each q point

    while True:    
        line = f.readline()                               
        if line.split(':')[0]=='lattice':
            break

    cell = [[0 for _ in range(3)] for _ in range(3)]
    for i in range(3):
        line = f.readline()
        cell[i] = map(float, re.findall(r"[-+]?\d*\.\d+|\d+", line))

    while True:    
        line = f.readline()                               
        if line.split(':')[0]=='atoms':
            break

    atoms = []
    for i in range(na):
        line = f.readline()
        symbol = re.split(r"\s+", line)[2]
        line = f.readline()
        xyz = map(float, re.findall(r"[-+]?\d*\.\d+|\d+", line))
        sx = xyz[0]*cell[0][0]+xyz[1]*cell[1][0]+xyz[2]*cell[2][0]
        sy = xyz[0]*cell[0][1]+xyz[1]*cell[1][1]+xyz[2]*cell[2][1]
        sz = xyz[0]*cell[0][2]+xyz[1]*cell[1][2]+xyz[2]*cell[2][2]
        sxyz = [sx, sy, sz]     # absolute xyz
        atom = Atom(symbol,sxyz,xyz)
        atoms.append(atom)
        line = f.readline()

    while True:    
        line = f.readline()                               
        if line.split(':')[0]=='phonon':
            break

    qw = [[0 for i in range(4)] for i in range(nq)]
    freq = [[0 for i in range(nb)] for i in range(nq)]
    mode = [[[[[0 for i in range(2)] for i in range(3)]
           for i in range(na)] for i in range(nb)] for i in range(nq)]
    dxyz = [[[[0 for i in range(6)]
           for i in range(na)] for i in range(nb)] for i in range(nq)]
    for iq in range(nq):
        line = f.readline()
        qw[iq][0:3] = map(float,re.findall(r"[-+]?\d*\.\d+|\d+", line))
        line = f.readline()
        #line = f.readline()
        qw[iq][3] = float(line.split()[1])/float(qtot)
        f.readline()
        for ib in range(nb):
            f.readline()
            line = f.readline()
            freq[iq][ib] = float(line.split()[1])
            freq[iq][ib] *= 33.3564  # convert from THz to cm-1
            f.readline()
            for ia in range(na):
                f.readline()
                for i in range(3):
                    line=f.readline()
                    mode[iq][ib][ia][i] = map(float,
                        re.findall(r"[-+]?\d*\.\d+|\d+", line))
                xyz = []
                for i in range(3):
                    for j in range(2):
                        xyz.append(mode[iq][ib][ia][i][j])
                for i in range(6):
                    dxyz[iq][ib][ia][i] = xyz[i]*qw[iq][3]**0.5
        f.readline()

    f.close()

    return atoms, cell, nq, qw, nb, freq, dxyz
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def get_outcar(file_outcar):
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Input: OUTCAR from VASP
# Output: phonon frequencies and modes (gamma point only)

    f = open(file_outcar,'r')
    full_text = f.read()
    f.close() 
    aux = re.compile('(?=Eigenvectors)(.*?)(?=============)',
          re.DOTALL).findall(full_text) 
    ind = [] 
    for i, line in enumerate(aux[0].split('\n')):
        if len(line.strip().split())<1:
            continue
        if line.strip().startswith('---'):
            ind.append(i)
            continue
        try:
            float(line.strip().split()[0])
        except ValueError:
            if line.strip().split()[0]!='X':
                ind.append(i)
        if len(ind)==3:
            break
    A = aux[0].split('\n')[ind[1]:ind[2]]
# Reads the frequencies and stores them in multidimensional array
#
    freq = []
    dxyz = []
    start = False
    reading = False
    for i in range(len(A)):
        aux = A[i].split()
        if re.search('cm-1', A[i]):
            disp = []
            start = True
            freq.append(float(aux[aux.index("cm-1")-1]))
        if len(aux) == 6:
            if (aux[0] != 'X'):
                disp.append([float(aux[3]),0.0,float(aux[4]),0.0,float(aux[5]),0.0])
                reading = True
        if (len(aux) != 6) and start and reading:
            dxyz.append(disp)
            start = False
            reading = False

    nq = 1            # gamma point only
    qw = [[0.0,0.0,0.0,1.0]]
    nb = len(freq)
    freq = [freq]
    dxyz = [dxyz]
    return nq, qw, nb, freq, dxyz
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def get_qe_ph_out(file_phout):
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Input: *.ph.out from Quantum Espresso (ph.x)
# Output: unit cell information
#
    f = open(file_phout, 'r')
    celldm = [0 for _ in range(6)]
    cell = [[0 for _ in range(3)] for _ in range(3)]
    atoms = []
    xyz = []
    symbol = []
    finishing = False
    for line in f:
        aux = line.split()
        if len(aux) == 0 and finishing:
            break
        if len(aux) == 0:
            continue
        if aux[0] == r"celldm(1)=":
            celldm[0] = float(aux[1])
            celldm[1] = float(aux[3])
            celldm[2] = float(aux[5])
        if aux[0] == r"celldm(4)=":
            celldm[3] = float(aux[1])
            celldm[4] = float(aux[3])
            celldm[5] = float(aux[5])
        if aux[0] == r"a(1)":
            cell[0][0] = float(aux[3])
            cell[0][1] = float(aux[4])
            cell[0][2] = float(aux[5])
        if aux[0] == r"a(2)":
            cell[1][0] = float(aux[3])
            cell[1][1] = float(aux[4])
            cell[1][2] = float(aux[5])
        if aux[0] == r"a(3)":
            cell[2][0] = float(aux[3])
            cell[2][1] = float(aux[4])
            cell[2][2] = float(aux[5])
        if len(aux) > 4 and re.match(r"tau.*", aux[2]) != None:
            xyz.append(map(float, re.findall(r"[-+]?\d*\.\d+|\d+", line))[2:5])
            symbol.append(aux[1])
            finishing = True

    if celldm[1] == 0.0:
       celldm[1] = celldm[0]
    else:
       celldm[1] = celldm[1]*celldm[0]
    if celldm[2] == 0.0:
       celldm[2] = celldm[2]*celldm[0]
    for i in range(len(xyz)):    # only orthorhombic cell for now
        x = [0 for _ in range(3)]
        for j in range(3):
            for k in range(3):
                x[k] = x[k] + celldm[k] * cell[k][j] * xyz[i][k] 
        for k in range(3):
            xyz[i][k] = x[k] 
    for i in range(len(symbol)):
        atom = Atom(symbol[i],xyz[i])
        atoms.append(atom)
    na = len(symbol)
    nb = 3*na

    return atoms, cell, nb
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


def get_qe_mesh_k(file_mesh):
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Input: mesh_k file generated by Quantum Espresso (kpoints.x) 
# Output: irreducible q points and degeneration (weight)
#
    f = open(file_mesh, 'r')
    qw = []
    line = f.readline()
    nq = int(line.split()[0])
    qtot = 0.0
    for i in range(nq):
        line = f.readline()
        qw.append(map(float,line.split()[1:5]))
        qtot += qw[i][3]
    f.close()
    for i in range(nq):
        qw[i][3] /= qtot    

    return nq, qw
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


def get_qe_matdyn_modes(file_matdyn, nq, qw, nb, na):
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Input: matdyn.modes from Quantum Espresso 
# Output: phonon frequencies and modes
#
    f = open(file_matdyn, 'r')
    freq = [[0 for i in range(nb)] for i in range(nq)]
    dxyz = [[[[0 for i in range(6)]
           for i in range(na)] for i in range(nb)] for i in range(nq)]
    for iq in range(nq):
        for _ in range(4):
            f.readline()     # discard the first four lines
        for ib in range(nb):
            line = f.readline()
            freq[iq][ib] = map(float, 
                         re.findall(r"[-+]?\d*\.\d+|\d+", line))[2]
            for ia in range(na):
                line = f.readline()
                dxyz[iq][ib][ia] = map(float, 
                        re.findall(r"[-+]?\d*\.\d+|\d+", line))
                for i in range(6):
                    dxyz[iq][ib][ia][i] *= qw[iq][3]**0.5
        f.readline()

    return freq, dxyz
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def get_gaussian(file_gaussian):
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Input: Gaussian output file (.log file)
# Output: atomic coordinates and phonon information
#
    f = open(file_gaussian, 'r')
    full_text = f.read()
    f.close() 

# Selects the text between 2 markers for positions (last appearance)
#
    aux = re.compile('(?=Standard orientation)(.*?)(?=Rotational constants)',
          re.DOTALL).findall(full_text)  
    chopped = aux[len(aux)-1].split('\n')

# Reads the atomic positions
#
    atoms = []
    for i in range(5,len(chopped)-2):
        aux = chopped[i].split()
        atom = Atom(int(aux[1]),map(float,aux[3:6]))
        atoms.append(atom)

# Selects the text between 2 markers for positions Frequencies
#
    aux = re.compile('(?=Frequencies)(.*?)Thermochemistry', 
          re.DOTALL).search(full_text)
    chopped = aux.group(1)
    aux = re.compile('(?=Frequencies)(.*?)-------------------', 
          re.DOTALL).findall(chopped)
    A = aux[0].split('\n')

# Reads the frequencies and stores them in multidimensional array
#
    freq = []
    dxyz = []
    for i in range(len(A)):
        aux = A[i].split()
        if re.search('Frequencies', A[i]):
            disp1 = []
            disp2 = []
            disp3 = []
            reading = True
            for j in range(2,5):
                freq.append(float(aux[j]))
        if len(aux) > 6:
            if (aux[0].isdigit()):
                disp1.append([float(aux[2]),0.0,float(aux[3]),0.0,float(aux[4]),0.0])
                disp2.append([float(aux[5]),0.0,float(aux[6]),0.0,float(aux[7]),0.0])
                disp3.append([float(aux[8]),0.0,float(aux[9]),0.0,float(aux[10]),0.0])
        if (len(aux) < 6) and reading:
            dxyz.append(disp1)
            dxyz.append(disp2)
            dxyz.append(disp3)
            reading = False

    dxyz = renorm(dxyz,atoms)
    cell=[[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]]
    nq = 1            # single molecule, gamma point only
    qw = [[0.0,0.0,0.0,1.0]]
    nb = len(freq)
    freq = [freq]
    dxyz = [dxyz]

    return atoms, cell, nq, qw, nb, freq, dxyz  
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def get_cp2k_mol(file_cp2k_mol):
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Input: *.mol from CP2K
# Output: atomic coordinates and phonon information
# Note: file is read line-by-line with all information retained
#
    f = open(file_cp2k_mol, 'r')
    full_text = f.read()
    f.close()
    aux = re.compile('(?<=\[FREQ\])(.*?)(?=\[FR-COORD\])',
          re.DOTALL).findall(full_text)
    A = aux[0].strip().split('\n')
    freq = []
    for i in range(len(A)):
        freq.append(float(A[i]))

    aux = re.compile('(?<=\[FR-COORD\])(.*?)(?=\[FR-NORM-COORD\])',
          re.DOTALL).findall(full_text)
    A = aux[0].strip().split('\n')
    atoms = []
    for i in range(len(A)):
        symbol = A[i].split()[0]
        xyz = map(float, A[i].split()[1:4])
        atom = Atom(symbol,xyz)
        atoms.append(atom)

    aux = re.compile('(?<=\[FR-NORM-COORD\])(.*)',
          re.DOTALL).findall(full_text)
    A = aux[0].strip().split('\n')
    A.append('vibration')
# Reads the frequencies and stores them in multidimensional array
#
    dxyz = []
    first_mode = True
    for i in range(len(A)):
        aux = A[i].split()
        if aux[0]=='vibration':
            if first_mode:
                disp = []
                first_mode = False
                continue
            else:
                dxyz.append(disp)
                disp = []
                continue
        else:
            disp.append([float(aux[0]),0.0,float(aux[1]),0.0,float(aux[2]),0.0])

    dxyz = renorm(dxyz,atoms)
    cell=[[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]]
    nq = 1            # gamma point only
    qw = [[0.0,0.0,0.0,1.0]]
    nb = len(freq)
    freq = [freq]
    dxyz = [dxyz]
    return atoms, cell, nq, qw, nb, freq, dxyz
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def get_dmol(file_dmol):
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Input: *.outmol from dmol
# Output: atomic coordinates and phonon information
#
    f = open(file_dmol, 'r')
    full_text = f.read()
    f.close()

    aux = re.compile('(?=Final Coordinates)(.*?)(?=Entering Properties Section)',
          re.DOTALL).findall(full_text)
    A = aux[0].strip().split('\n')
    atoms = []
    for i in range(3,len(A)-4):
        aux = A[i].split()
        symbol = (aux[1])
        xyz = (map(float, aux[2:5]))
        atom = Atom(symbol,xyz)
        atoms.append(atom)

    aux = re.compile('(?=vibrational frequencies)(.*?)(?=Frequencies \(cm-1\) and normal modes)',
          re.DOTALL).findall(full_text)
    A = aux[0].strip().split('\n')
    freq = []
    for i in range(2,len(A)):
        freq.append(float(A[i].split()[2]))

    aux = re.compile('(?=Frequencies \(cm-1\) and normal modes)(.*?)(?=STANDARD THERMODYNAMIC QUANTITIES)',
          re.DOTALL).findall(full_text)
    A = aux[0].strip().split('\n')
    na = len(atoms)
    nb = len(freq)
    nc = 9
    np = int(nb/nc)+1
    dxyz = [[[0 for i in range(6)]
           for i in range(na)] for i in range(nb)]
    for ip in range(np):
        for ia in range(na):
            i=ip*(3*na+4)+3+ia*3
            if ip==np-1:
                ni = nb%nc
            else:
                ni = nc
            aux = map(float, A[i].split()[2:ni+2])
            for ii in range(ni):
                j = ip*nc + ii
                dxyz[j][ia][0]=aux[ii]
            aux = map(float, A[i+1].split()[1:ni+1])
            for ii in range(ni):
                j = ip*nc + ii
                dxyz[j][ia][2]=aux[ii]
            aux = map(float, A[i+2].split()[1:ni+1])
            for ii in range(ni):
                j = ip*nc + ii
                dxyz[j][ia][4]=aux[ii]

    dxyz = renorm(dxyz,atoms)
    cell=[[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]]
    nq = 1            # gamma point only
    qw = [[0.0,0.0,0.0,1.0]]
    nb = len(freq)
    freq = [freq]
    dxyz = [dxyz]
    return atoms, cell, nq, qw, nb, freq, dxyz
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def get_nwchem(file_nwchem):
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Input: *-freq.out from nwchem
# Output: atomic coordinates and phonon information
#
    f = open(file_nwchem, 'r')
    full_text = f.read()
    f.close()

    aux = re.compile('(?=Atom information)(.*?)(?=MASS-WEIGHTED)',
          re.DOTALL).findall(full_text)
    A = aux[0].strip().split('\n')
    atoms = []
    for i in range(3,len(A)-6):
        aux = A[i].replace('D','E').split()
        symbol = aux[0]
        xyz = map(float, aux[2:5])
        atom = Atom(symbol,xyz)
        atoms.append(atom)

    aux = re.compile('(?=\(Frequencies expressed in cm-1\))(.*?)(?=--------------)',
          re.DOTALL).findall(full_text)
    A = aux[0].strip().split('\n')
    na = len(atoms)
    nb = 3*na
    nc = 6
    np = int(nb/nc)+1
    freq = [0 for i in range(nb)]
    dxyz = [[[0 for i in range(6)]
           for i in range(na)] for i in range(nb)]
    for ip in range(np):
        ib=ip*(3*na+5)+1+3
        if ip==np-1:
            ni = nb%nc
            if ni==0:
                break
        else:
            ni = nc
        aux = map(float, A[ib].split()[1:ni+1])
        for ii in range(ni):
            j = ip*nc + ii
            freq[j]=aux[ii]
        for ia in range(na):
            i=ip*(3*na+5)+1+5+ia*3
            for jj in range(3):
                aux = map(float, A[i+jj].split()[1:ni+1])
                for ii in range(ni):
                    j = ip*nc + ii
                    dxyz[j][ia][2*jj]=aux[ii]

    dxyz = renorm(dxyz,atoms)
    cell=[[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]]
    nq = 1            # gamma point only
    qw = [[0.0,0.0,0.0,1.0]]
    nb = len(freq)
    freq = [freq]
    dxyz = [dxyz]
    return atoms, cell, nq, qw, nb, freq, dxyz
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def get_orca(file_orca):
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Input: *.hess from ORCA
# Output: atomic coordinates and phonon information
#
    f = open(file_orca, 'r')
    full_text = f.read()
    f.close()

    aux = re.compile('(?=\$atoms)(.*?)(?=\$actual_temperature)',
          re.DOTALL).findall(full_text)
    A = aux[0].strip().split('\n')
    atoms = []
    for i in range(2,len(A)):
        aux = A[i].split()
        symbol = aux[0]
        xyz = map(float, aux[2:5])
        atom = Atom(symbol,xyz)
        atoms.append(atom)

    na = len(atoms)
    nb = 3*na
    freq = [0 for i in range(nb)]
    aux = re.compile('(?=\$vibrational_frequencies)(.*?)(?=\$normal_modes)',
          re.DOTALL).findall(full_text)
    A = aux[0].strip().split('\n')
    for i in range(nb):
        freq[i] = float(A[i+2].split()[1])

    nc = 6
    np = int(nb/nc)+1
    dxyz = [[[0 for i in range(6)]
           for i in range(na)] for i in range(nb)]
    aux = re.compile('(?=\$normal_modes)(.*?)(?=\#)',
          re.DOTALL).findall(full_text)
    A = aux[0].strip().split('\n')
    for ip in range(np):
        if ip==np-1:
            ni = nb%nc
            if ni==0:
                break
        else:
            ni = nc
        for ia in range(na):
            i=ip*(3*na+1)+3+ia*3
            for jj in range(3):
                aux = map(float, A[i+jj].split()[1:ni+1])
                for ii in range(ni):
                    j = ip*nc + ii
                    dxyz[j][ia][2*jj]=aux[ii]

    dxyz = renorm(dxyz,atoms)
    cell=[[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]]
    nq = 1            # gamma point only
    qw = [[0.0,0.0,0.0,1.0]]
    nb = len(freq)
    freq = [freq]
    dxyz = [dxyz]
    return atoms, cell, nq, qw, nb, freq, dxyz
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def get_castep(file_castep):
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Input: *.phonon from CASTEP 
# Output: atomic coordinates and phonon information
#
    f = open(file_castep, 'r')
    
    f.readline()
    line = f.readline()
    na = int(re.findall(r"\d+", line)[0])
    line = f.readline()
    nb = int(re.findall(r"\d+", line)[0])
    line = f.readline()
    nq = int(re.findall(r"\d+", line)[0])

    for _ in range(4):
        f.readline()
    cell = [[0 for _ in range(3)] for _ in range(3)]
    for i in range(3):
        line = f.readline()
        cell[i] = map(float, line.split())
    f.readline()
    atoms = []
    for i in range(na):
        line = f.readline()
        xyz = map(float, re.findall(r"[-+]?\d*\.\d+|\d+", line)[1:4])
        sx = xyz[0]*cell[0][0]+xyz[1]*cell[1][0]+xyz[2]*cell[2][0]
        sy = xyz[0]*cell[0][1]+xyz[1]*cell[1][1]+xyz[2]*cell[2][1]
        sz = xyz[0]*cell[0][2]+xyz[1]*cell[1][2]+xyz[2]*cell[2][2]
        sxyz = [sx, sy, sz]     # absolute xyz
        symbol = re.split(r"\s+", line)[5]    
        atom = Atom(symbol,sxyz,xyz)
        atoms.append(atom)

    f.readline()
    qw = [[0 for i in range(4)] for i in range(nq)]
    freq = [[0 for i in range(nb)] for i in range(nq)]
    dxyz = [[[[0 for i in range(6)]
           for i in range(na)] for i in range(nb)] for i in range(nq)]
    iq = 0
    while True:
        line = f.readline()
        iiq = int(line.split('=')[1].split()[0])-1
        if iiq==iq:
            qw[iq] = map(float, line.split('=')[1].split()[1:5])
            for ib in range(nb):
                line = f.readline()
                freq[iq][ib] = float(line.split()[1])
            f.readline()
            f.readline()
            for ib in range(nb):
                for ia in range(na):
                    line = f.readline()
                    aux = map(float, line.split()[2:8])
                    for i in range(6):
                        dxyz[iq][ib][ia][i] = aux[i]*qw[iq][3]**0.5
            iq += 1
            if iq==nq:
                break
        else:
            #print 'ignore duplicated q points'
            for ib in range(nb):
                line = f.readline()
            f.readline()
            f.readline()
            for ib in range(nb):
                for ia in range(na):
                    line = f.readline()
    f.close()
    return atoms, cell, nq, qw, nb, freq, dxyz
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def get_aclimax(file_aclimax):
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#
    f = open(file_aclimax, 'r')
    full_text = f.read()
    f.close()

    aux = re.compile('(?=BEGIN ATOMS)(.*?)(?=END ATOMS)',
          re.DOTALL).findall(full_text)
    A = aux[0].strip().split('\n')
    atoms = []
    for i in range(1,len(A)):
        if A[i].isspace():
            continue
        aux = A[i].split()
        symbol = aux[1]
        xyz = map(float, aux[4:7])
        atom = Atom(symbol,xyz)
        atoms.append(atom)

    aux = re.compile('(?=BEGIN FREQUENCIES)(.*?)(?=END FREQUENCIES)',
          re.DOTALL).findall(full_text)
    A = aux[0].strip().split('!MODE# FREQUENCY')
    freq = []
    dxyz = []
    for i in range(1,len(A)): 
        aux = os.linesep.join([s for s in A[i].splitlines() if s])
        freq.append(float(aux.split('\n')[0].split()[1]))
        xyz = []
        for ia in range(len(atoms)):
            mode = aux.split('\n')[ia+1].split()
            xyz.append([float(mode[3]),0.0,float(mode[4]),0.0,float(mode[5]),0.0])
        dxyz.append(xyz)

    cell=[[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]]
    nq = 1            # gamma point only
    qw = [[0.0,0.0,0.0,1.0]]
    nb = len(freq)
    freq = [freq]
    dxyz = [dxyz]

    return atoms, cell, nq, qw, nb, freq, dxyz
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


def write_climax(argv, atoms, cell, nq, qw, nb, freq, dxyz):
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Write aclimax/oclimax file
#
    if argv[-2]=='-a' or argv[-1]=='-a':
        tag = 'a'
        if argv[-2]=='-a':
            output_file = argv[-1]+'.aclimax'
        else:
            output_file = 'out.aclimax'
    elif argv[-2]=='-o' or argv[-1]=='-o':
        tag = 'o'
        if argv[-2]=='-o':
            output_file = argv[-1]+'.oclimax'
        else:
            output_file = 'out.oclimax'
    else:
        tag = 'a'
        output_file = 'out.aclimax'

    if tag=='o' and sum(map(sum,cell))==0:
        print "Error: non-periodic system, cannot write oclimax file. Try aclimax file."
        sys.exit()

    f = open(output_file, 'w')

    if tag == 'o':
        print >> f, "BEGIN LATTICE"
        print >> f, '%12.6f' % cell[0][0], '%12.6f' % cell[0][1], '%12.6f' % cell[0][2]
        print >> f, '%12.6f' % cell[1][0], '%12.6f' % cell[1][1], '%12.6f' % cell[1][2]
        print >> f, '%12.6f' % cell[2][0], '%12.6f' % cell[2][1], '%12.6f' % cell[2][2]
        print >> f, "END LATTICE"
        print >> f
        print >> f
    
    print >> f, "BEGIN ATOMS"
    for i in range(len(atoms)):
        if tag == 'o':
            print >> f, '%8d' % (i+1), '%4s' % atoms[i].symbol,'%4d' % atoms[i].Z,\
                  '%12.6f' % atoms[i].mass,'%12.6f' % atoms[i].pos[0],\
                  '%12.6f' % atoms[i].pos[1],'%12.6f' % atoms[i].pos[2],\
                  '%12.6f' % atoms[i].xc_tot,'%12.6f' % atoms[i].xc_inc,\
                  '%12.6f' % atoms[i].b_coh
        else:
            print >> f, '%8d' % (i+1), '%4s' % atoms[i].symbol,'%4d' % atoms[i].Z,\
                  '%12.6f' % atoms[i].mass,'%12.6f' % atoms[i].pos[0],\
                  '%12.6f' % atoms[i].pos[1],'%12.6f' % atoms[i].pos[2],\
                  '%12.6f' % atoms[i].xc_tot
    
    print >> f, "END ATOMS"     
    print >> f
    print >> f
    print >> f, "BEGIN FREQUENCIES"
    for iq in range(nq):
        for ib in range(nb):
            print >> f, "!MODE# FREQUENCY"
            print >> f, '%8d' % (iq*nb+ib+1),' %12.6f' % freq[iq][ib]
            if tag == 'o':
                print >> f, '%12.6f' % qw[iq][0],' %12.6f' % qw[iq][1], \
                        '%12.6f' % qw[iq][2],' %12.6f' % qw[iq][3]
            else:
                print >> f
            for ia in range(len(atoms)):
                if tag == 'o':
                    print >> f, '%8d'% (ia+1), '%4s' % atoms[ia].symbol, \
                             '%4d'% atoms[ia].Z, \
                             '%12.6f' % dxyz[iq][ib][ia][0], \
                             '%12.6f' % dxyz[iq][ib][ia][1], \
                             '%12.6f' % dxyz[iq][ib][ia][2], \
                             '%12.6f' % dxyz[iq][ib][ia][3], \
                             '%12.6f' % dxyz[iq][ib][ia][4], \
                             '%12.6f' % dxyz[iq][ib][ia][5]
                else:
                    dx = cmp(dxyz[iq][ib][ia][0],0)*(dxyz[iq][ib][ia][0]**2+dxyz[iq][ib][ia][1]**2)**0.5
                    dy = cmp(dxyz[iq][ib][ia][2],0)*(dxyz[iq][ib][ia][2]**2+dxyz[iq][ib][ia][3]**2)**0.5
                    dz = cmp(dxyz[iq][ib][ia][4],0)*(dxyz[iq][ib][ia][4]**2+dxyz[iq][ib][ia][5]**2)**0.5
                    print >> f, '%8d'% (ia+1), '%4s' % atoms[ia].symbol, \
                             '%4d'% atoms[ia].Z, \
                             '%12.6f' % dx, '%12.6f' % dy, '%12.6f' % dz

    print >> f, "END FREQUENCIES"        
    
    f.close()
    unix2dos(output_file)
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def write_phonon(argv, atoms, cell, nq, qw, nb, freq, dxyz):
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Write phonon file
#
    if argv[-2]=='-p':
        output_file = argv[-1]+'_gamma.phonon'
    else:
        output_file = 'out_gamma.phonon'

    if nq==1:
        igam = 0
    else:
        for iq in range(nq):
            if (qw[iq][0]**2+qw[iq][1]**2+qw[iq][2]**2)<1.0e-8:
                igam = iq
                break
    na = len(atoms)

    f = open(output_file, 'w')
    print >> f, " BEGIN header"
    print >> f, " Number of ions", na
    print >> f, " Number of branches", nb
    print >> f, " Number of wavevectors  1"
    print >> f, " Frequencies in         cm-1"
    print >> f, " IR intensities in      (D/A)**2/amu"
    print >> f, " Raman intensities in   A**4"
    print >> f, " Unit cell vectors (A)"
    print >> f, '%12.6f' % cell[0][0],'%12.6f' % cell[0][1],'%12.6f' % cell[0][2]
    print >> f, '%12.6f' % cell[1][0],'%12.6f' % cell[1][1],'%12.6f' % cell[1][2]
    print >> f, '%12.6f' % cell[2][0],'%12.6f' % cell[2][1],'%12.6f' % cell[2][2]
    print >> f, " Fractional Co-ordinates"
    for ia in range(na):
        print >> f, '%5d' % (ia+1),'%12.6f' % atoms[ia].frc[0],'%12.6f' % atoms[ia].frc[1],'%12.6f' % atoms[ia].frc[2],'%4s' % atoms[ia].symbol,'%12.6f' % atoms[ia].mass
    print >> f, " END header"
    print >> f, " q-pt=    1   0.000000  0.000000  0.0000      1.0"
    for ib in range(nb):
        print >> f, '%7d' % (ib+1),'%15.6f' % freq[igam][ib]
    print >> f, "                        Phonon Eigenvectors"
    print >> f, "Mode Ion                X                                   Y                                   Z"
    for ib in range(nb):
        for ia in range(na):
            print >> f, '%4d' % (ib+1),'%3d' % (ia+1), \
                     '%15.12f' % (dxyz[igam][ib][ia][0]/qw[igam][3]**0.5), \
                     '%15.12f' % (dxyz[igam][ib][ia][1]/qw[igam][3]**0.5), \
                     '%19.12f' % (dxyz[igam][ib][ia][2]/qw[igam][3]**0.5), \
                     '%15.12f' % (dxyz[igam][ib][ia][3]/qw[igam][3]**0.5), \
                     '%19.12f' % (dxyz[igam][ib][ia][4]/qw[igam][3]**0.5), \
                     '%15.12f' % (dxyz[igam][ib][ia][5]/qw[igam][3]**0.5)

    f.close()
    unix2dos(output_file)

#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def write_xyz(argv, atoms, cell, nq, qw, nb, freq, dxyz):
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Write xyz file
#
    if argv[-2]=='-x':
        output_file = argv[-1]+'_gamma.xyz'
    else:
        output_file = 'out_gamma.xyz'

    if nq==1:
        igam = 0
    else:
        for iq in range(nq):
            if (qw[iq][0]**2+qw[iq][1]**2+qw[iq][2]**2)<1.0e-8:
                igam = iq
                break
    na = len(atoms)

    f = open(output_file, 'w')

    for ib in range(nb):
        print >> f, '%3d' % na
        print >> f, '%6s' % "Mode   ", '%4d' % (ib+1), '%3s' % ", ", '%8.3f' % freq[igam][ib], '%5s' % "1/cm"
        for ia in range(na):
            print >> f, '%2s' % atoms[ia].symbol,'%8.4f' % atoms[ia].pos[0],\
                     '%8.4f' % atoms[ia].pos[1],'%8.4f' % atoms[ia].pos[2],\
                     '%8.4f' % (dxyz[igam][ib][ia][0]/qw[igam][3]**0.5), \
                     '%8.4f' % (dxyz[igam][ib][ia][2]/qw[igam][3]**0.5), \
                     '%8.4f' % (dxyz[igam][ib][ia][4]/qw[igam][3]**0.5)

    f.close()
    unix2dos(output_file)
#
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


#=============================================================================
# Main program starts here
#

if len(sys.argv)>2 and sys.argv[1] in ['-c', '-C', '-castep', '-CASTEP']: # from CASTEP
    atoms, cell, nq, qw, nb, freq, dxyz = get_castep(sys.argv[2])

elif len(sys.argv)>3 and sys.argv[1] in ['-vp', '-VP']:  # from VASP Phonopy
    atoms, cell = get_poscar(sys.argv[2])
    nq, qw, nb, freq, dxyz = get_phonopy(sys.argv[3])

elif len(sys.argv)>3 and sys.argv[1] in ['-vo', '-VO']:  # from VASP OUTCAR
    atoms, cell = get_poscar(sys.argv[2])
    nq, qw, nb, freq, dxyz = get_outcar(sys.argv[3])

elif len(sys.argv)>2 and sys.argv[1] in ['-2k', '-cp2k']: # from CP2K mol file
    atoms, cell, nq, qw, nb, freq, dxyz = get_cp2k_mol(sys.argv[2])

elif len(sys.argv)>2 and sys.argv[1] in ['-yaml', '-rmg', '-RMG']: # from RMG
    atoms, cell, nq, qw, nb, freq, dxyz = get_mesh_yaml(sys.argv[2])

elif len(sys.argv)>4 and sys.argv[1] in ['-qe', '-QE']:  # from Quantum Espresso
    atoms, cell, nb = get_qe_ph_out(sys.argv[2])
    nq, qw = get_qe_mesh_k(sys.argv[3])
    freq, dxyz = get_qe_matdyn_modes(sys.argv[4], nq, qw, nb, len(atoms))

elif len(sys.argv)>2 and sys.argv[1] in ['-g', '-G', '-gaussian', '-GAUSSIAN']: # from Gaussian
    atoms, cell, nq, qw, nb, freq, dxyz = get_gaussian(sys.argv[2])

elif len(sys.argv)>2 and sys.argv[1] in ['-d', '-D', '-dmol', '-DMol']: # from DMol
    atoms, cell, nq, qw, nb, freq, dxyz = get_dmol(sys.argv[2])

elif len(sys.argv)>2 and sys.argv[1] in ['-n', '-N', '-nwchem', '-NWChem']: # from NWChem
    atoms, cell, nq, qw, nb, freq, dxyz = get_nwchem(sys.argv[2])

elif len(sys.argv)>2 and sys.argv[1] in ['-o', '-orca']: # from ORCA
    atoms, cell, nq, qw, nb, freq, dxyz = get_orca(sys.argv[2])

elif len(sys.argv)>2 and sys.argv[1] in ['-a', '-aclimax']: # from old/non-standard aclimax
    atoms, cell, nq, qw, nb, freq, dxyz = get_aclimax(sys.argv[2])

else:
    print "********************************************************************************************"
    print "If you are running through Docker, the command line should be:"
    print "Linux/Mac: oclimax convert -input_tag input_file1 [input_file2 ... -output_tag output_file]"
    print "Windows: oclimax.bat convert -input_tag input_file1 [input_file2 ... -output_tag output_file]"
    print "********************************************************************************************"
    print "-input_tag and the corresponding input files can be:"
    print "-c: CASTEP              input file(s): *.phonon"
    print "-vp: VASP+Phonopy       input file(s): POSCAR-unitcell mesh.yaml"
    print "-vo: VASP               input file(s): POSCAR OUTCAR"
    print "-qe: Quantum Espresso   input file(s): *.ph.out mesh_k matdyn.modes"
    print "-yaml: Phonopy/RMG      input file(s): mesh.yaml (new format containing atomic coordinates)"
    print "-cp2k: CP2K             input file(s): *.mol"
    print "-nwchem: NWChem         input file(s): *-freq.out"
    print "-g: Gaussian            input file(s): *.log"
    print "-o: ORCA                input file(s): *.hess"
    print "-d: DMol                input file(s): *.outmol"
    print "-a: aclimax             input file(s): *.aclimax file with old/non-standard format"
    print "********************************************************************************************"
    print "-output_tag can be the fololwing, and -a is the default"
    print "-a: the old aclimax format for incoherent calculation only."
    print "-o: the new oclimax format which can be used for both incoherent and coherent calculations."
    print "-p: phonon file including the gamma point modes only for visualization with JMol."
    print "-x: xyz file including the gamma point modes only for visualization with JMol."
    print "Note -o and -p are only available for periodic systems."
    print "********************************************************************************************"
    print "The name of the output file (excluding the suffix) can be specified after the tag."
    print "The default output is out.*"
    print "********************************************************************************************"
    print "Warning: Format of the input files may vary." 
    print "Users may make corresponding changes in this script or contact YQ Cheng (chengy@ornl.gov)."
    print "********************************************************************************************"
    sys.exit()

if sys.argv[-2]=='-p' or sys.argv[-1]=='-p':
    if sum(map(sum,cell))==0:
        print "Error: non-periodic system, cannot write phonon file. Try xyz file."
        sys.exit()
    write_phonon(sys.argv, atoms, cell, nq, qw, nb, freq, dxyz)
elif sys.argv[-2]=='-x' or sys.argv[-1]=='-x':
    write_xyz(sys.argv, atoms, cell, nq, qw, nb, freq, dxyz)
else:
    write_climax(sys.argv, atoms, cell, nq, qw, nb, freq, dxyz)


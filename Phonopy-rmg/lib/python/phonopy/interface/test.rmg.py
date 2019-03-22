# Written for RMG by zjyx, at Apr/2016.

'''
 Revision history:
   1. @version 1.10.10:
       change import atoms to import PhonopyAtoms, at Aug/2016
       add option 'unoccupied_states_per_kpoint', at Jan/2017

******** TODO List ***********
   1. take care of tags who may not exist
******** end *****************
'''

import os
import sys
import numpy as np


#get forces; drift forces mean total forces from outside
from phonopy.file_IO import iter_collect_forces, get_drift_forces

#get relative position in units of 1(length of cell)
from phonopy.interface.vasp import get_scaled_positions_lines

#Bohr radius
from phonopy.units import Bohr

#check if it is a fractional value
from phonopy.cui.settings import fracval

#get attibutes of atoms; symbol map is like: "H":1...
from phonopy.structure.atoms import PhonopyAtoms as Atoms
from phonopy.structure.atoms import symbol_map


# find forces and extract non-zero mean forces
def parse_set_of_forces(num_atoms, forces_filenames):
    hook = 'Ion  Species'
    force_sets = []
    for filename in forces_filenames:
        rmg_forces = iter_collect_forces( filename,
                                          num_atoms,
                                          hook,
                                          [7, 8, 9],
                                          word='@ION')
        if not rmg_forces:
            return []

        drift_force = get_drift_forces(rmg_forces)
        force_sets.append(np.array(rmg_forces) - drift_force)
        
    return force_sets


# read rmg input files
def read_rmg(filename):

    rmg_in = RmgIn(open(filename).readlines())
    tags = rmg_in.get_tags()
    #now only works for tetragonal struture
    lattice = np.array([[tags['a_length'], 0.0, 0.0],
                        [0.0, tags['b_length'], 0.0],
                        [0.0, 0.0, tags['c_length']]])
    positions = [pos[1] for pos in tags['atoms']]
    species = [pos[0] for pos in tags['atoms']]
    kpoint_mesh = tags['kpoint_mesh']
    wavefunction_grid = tags['wavefunction_grid']
    others = tags['others']
    #mass_map = {}
    #pp_map = {}
    #for vals in tags['atomic_species']:
    #    mass_map[vals[0]] = vals[1]
    #    pp_map[vals[0]] = vals[2]
    #masses = [mass_map[x] for x in species]
    #pp_all_filenames = [pp_map[x] for x in species]

    #unique_species = list(set(species))
    unique_species = []
    for x in species:
        if x not in unique_species:
            unique_species.append(x)

    # find atoms not in periodical table, mark with negative number
    numbers = []
    is_unusual = False
    for x in species:
        if x in symbol_map:
            numbers.append(symbol_map[x])
        else:
            numbers.append(-unique_species.index(x))
            is_unusual = True

    if is_unusual:
        positive_numbers = []
        for n in numbers:
            if n > 0:
                if n not in positive_numbers:
                    positive_numbers.append(n)
    
        available_numbers = range(1, 119)
        for pn in positive_numbers:
            available_numbers.remove(pn)
        
        for i, n in enumerate(numbers):
            if n < 1:
                #???? not understant what is this
                numbers[i] = available_numbers[-n]

        cell = Atoms(numbers=numbers,
                     masses=masses,
                     cell=lattice,
                     scaled_positions=positions)
                     # scaled positions mean relative pos
    else:
        cell = Atoms(numbers=numbers,
                     cell=lattice,
                     scaled_positions=positions)

    #unique_symbols = list(set(cell.get_chemical_symbols()))
    unique_symbols = []
    for i, symbol in enumerate(cell.get_chemical_symbols()):
        if symbol not in unique_symbols:
            unique_symbols.append(symbol)

    return cell, tags


# update tags for supercells
def update_rmg_tags(tags, dim_lst):
    grid = tags['wavefunction_grid']
    mesh = tags['kpoint_mesh']
    nspk = tags['unoccupied_states_per_kpoint']
    grid_new = []
    mesh_new = []
    if grid is not None:
        for i in range(len(grid)):
            grid_new.append(grid[i]*dim_lst[i])
        tags['wavefunction_grid'] = grid_new
    # minimal value for mesh is '1 1 1'
    if mesh is not None:
        for i in range(len(mesh)):
            if mesh[i] > dim_lst[i]:
                mesh_new.append(mesh[i]/dim_lst[i])
            else:
                mesh_new.append( 1 )
        tags['kpoint_mesh'] = mesh_new
    if nspk is not None:
        tags['unoccupied_states_per_kpoint'] = nspk*dim_lst[0]*dim_lst[1]*dim_lst[2]

    return tags


def write_rmg(filename, cell, tags):
    f = open(filename, 'wb')
    f.write(get_rmg_structure(cell, tags))
    f.close()

# write supercell input files with displacement
def write_supercells_with_displacements(supercell,
                                        tags,
                                        cells_with_displacements,
                                        pre_pathname="supercell",
                                        width=3):
    supercell_dir = 'supercells'
    # write supercell in parent directory
    write_rmg("supercell.in", supercell, tags)
    if not os.path.exists(supercell_dir):
        os.mkdir(supercell_dir)
    os.chdir(supercell_dir)

    # write supercell in directory supercell-000
    path_orig = "{pre_pathname}-{0:0{width}}".format(
                0,
                pre_pathname=pre_pathname,
                width=width)

    if not os.path.exists(path_orig):
        os.mkdir(path_orig)
    os.chdir(path_orig)
    write_rmg("supercell.in", supercell, tags)
    os.chdir('..')

    # write supercells with perturbations
    for i, cell in enumerate(cells_with_displacements):
        if cell is not None:
            pathname = "{pre_pathname}-{0:0{width}}".format(
                i + 1,
                pre_pathname=pre_pathname,
                width=width)
            if not os.path.exists(pathname):
                os.mkdir(pathname)
            os.chdir(pathname)
            write_rmg('supercell.in', cell, tags)
            os.chdir('..')


# read the structure of the given material
def get_rmg_structure(cell, tags):

    lattice = cell.get_cell()
    grid = tags['wavefunction_grid']
    crds_type = tags['atomic_coordinate_type']
    uspk = tags['unoccupied_states_per_kpoint']
    mesh = tags['kpoint_mesh']
    units = tags['crds_units']
    movable = tags['movable']
    others = tags['others']
    positions = cell.get_scaled_positions()
    masses = cell.get_masses()
    chemical_symbols = cell.get_chemical_symbols()
    unique_symbols = []
    atomic_species = []
    # NOTE: try to use function SET
    for symbol, m in zip(chemical_symbols, masses):
        if symbol not in unique_symbols:
            unique_symbols.append(symbol)
            atomic_species.append((symbol, m))

    
    lines = "\n"
    lines += "#"*32+'\n'
    lines += "# Input info for RMG:\n"
    lines += "#     Species: %s\n"%(unique_symbols)
    lines += "#     Number of species: %d\n"%(len(atomic_species))
    # NOTE: avoid using 'atoms' in this line
    lines += "#     Number of ions: %d\n"%(len(positions))
    lines += "#"*32+'\n'
    lines += "\n"*4
    lines += 'wavefunction_grid="%d %d %d"\n\n'%(grid[0], grid[1], grid[2])
    lines += 'kpoint_mesh="%d %d %d"\n\n'%(mesh[0], mesh[1], mesh[2])
    lines += 'a_length="%.12f"\n\n'%(lattice[0][0])
    lines += 'b_length="%.12f"\n\n'%(lattice[1][1])
    lines += 'c_length="%.12f"\n\n'%(lattice[2][2])
    lines += 'crds_units="%s"\n\n'%(units)
    # length_units may show up twice, for the reason of compatibility
    lines += 'length_units="%s"\n\n'%(units)
    lines += 'atomic_coordinate_type="%s"\n\n'%(crds_type)

    #*******    for tags may not exist  **********
    if uspk is not None:
        lines += 'unoccupied_states_per_kpoint="%d"\n\n'%(uspk)
    #*******    block end   **********
    others_str = "".join(others)
    lines += others_str
    lines += "atoms = \n"
    lines += '"\n'
    pos_lst = positions.tolist()
    for i, (symbol, pos_line) in enumerate(zip(chemical_symbols, pos_lst)):
        # need to think a better way to get movable here,0 is temp value
        lines += "%2s" % symbol
        for x in pos_line:
            lines += "%20.16f"%x
        lines += '%5d\n'%(1)
        #if i < len(chemical_symbols) - 1:
        #    lines += "\n"
    lines += '"'

    return lines
    
class RmgIn:

    def __init__(self, lines):
        self._set_methods = {'a_length': self._set_a_length,
                             'b_length': self._set_b_length,
                             'c_length': self._set_c_length,
                             'wavefunction_grid': self._set_grid,
                             'atomic_coordinate_type': self._set_crd_type,
                             'kpoint_mesh': self._set_kpoint_mesh,
                             'crds_units': self._set_units,
                             'atoms': self._set_positions,
                             'unoccupied_states_per_kpoint': self._set_uspk,
                             'others': self._set_others}
        self._tags = {'a_length': None,
                      'b_length': None,
                      'c_length': None,
                      'wavefunction_grid': None,
                      'atomic_coordinate_type': None,
                      'kpoint_mesh': None,
                      'crds_units': None,
                      'atoms': None,
                      'unoccupied_states_per_kpoint': None,
                      'movable': None,
                      'pos_len': None,
                      'others': None}

        # values are just tmp iterations of tags, similar to key-value
        self._values = None
        self._collect(lines)
        #print self._tags
        #print self._values

    def get_tags(self):
        #print self._tags
        return self._tags

    def _collect(self, lines):
        elements = {}
        elements['others'] = []
        tag = None
        for line_num, line_tmp in enumerate(lines):
            # skip comment lines
            line = line_tmp.split('#')[0]
            if len(line) < 2:
                continue

            if 'atoms' in line:
                line_replaced = line.replace('=', ' ').replace('"',' ')
                words = line_replaced.split()
                # length of pos info
                self._tags['pos_len'] = len(lines[line_num+2].split())
            elif 'crds_units' in line:
                line_replaced = line.replace('=', ' ').replace('"',' ')
                words = line_replaced.split()[:]
            elif 'a_length' in line:
                line_replaced = line.replace('=', ' ').replace('"',' ')
                words = line_replaced.split()[:]
            elif 'b_length' in line:
                line_replaced = line.replace('=', ' ').replace('"',' ')
                words = line_replaced.split()[:]
            elif 'c_length' in line:
                line_replaced = line.replace('=', ' ').replace('"',' ')
                words = line_replaced.split()[:]
            elif 'wavefunction_grid' in line:
                line_replaced = line.replace('=', ' ').replace('"',' ')
                words = line_replaced.split()[:]
            elif 'atomic_coordinate_type' in line:
                line_replaced = line.replace('=', ' ').replace('"',' ')
                words = line_replaced.split()[:]
            elif 'kpoint_mesh' in line:
                line_replaced = line.replace('=', ' ').replace('"',' ')
                words = line_replaced.split()[:]
            elif 'unoccupied_states_per_kpoint' in line:
                line_replaced = line.replace('=', ' ').replace('"',' ')
                words = line_replaced.split()[:]
            else:
                line_others = 'others ' + line
                words = line_others.split()

            # we first construct dict elements with blank keys and values
            # then once we find a new key, we will read all following lines
            # unless we meet another new key. Things are different for 
            # others and atoms
            for val in words:
                if tag == 'atoms':
                    if (val != 'others') and (val != '"'):
                        elements[tag].append(val)
                elif val in self._set_methods:
                    tag = val
                    if tag != 'others':
                        elements[tag] = []
                    for val_tmp in words[1:]:
                        elements[tag].append(val_tmp)
                    if tag == 'others':
                        elements[tag].append('\n')

        #for tag in ['any tag not considered in above lines']:
        #    if tag not in elements:
        #        print('%s is not found in the input file!'% tag)
        #        sys.exit(1)

        # these values need to be found first,
        # because they are used in other functions
        for tag, self._values in elements.iteritems():
            if (tag == 'units' or tag == 'atomic_coordinate_type' or
                tag == 'a_length' or tag == 'b_length' or tag == 'c_length'):
                self._set_methods[tag]()

        for tag, self._values in elements.iteritems():
            if (tag != 'units' and tag != 'atomic_coordinate_type' and
                tag != 'a_length' and tag != 'b_length' and tag != 'c_length'):
                self._set_methods[tag]()

    def _set_units(self):
        self._tags['crds_units'] = self._values[0]

    def _set_a_length(self):
        units = self._tags['crds_units']
        if units == 'angstrom':
            factor = 1.0/Bohr
        else:
            factor = 1.0
        a_length_tmp = float(self._values[0])
        self._tags['a_length'] = a_length_tmp*factor

    def _set_b_length(self):
        units = self._tags['crds_units']
        if units == 'angstrom':
            factor = 1.0/Bohr
        else:
            factor = 1.0
        b_length_tmp = float(self._values[0])
        self._tags['b_length'] = b_length_tmp*factor

    def _set_c_length(self):
        units = self._tags['crds_units']
        if units == 'angstrom':
            factor = 1.0/Bohr
        else:
            factor = 1.0
        c_length_tmp = float(self._values[0])
        self._tags['c_length'] = c_length_tmp*factor

    def _set_crd_type(self):
        tmp = self._values
        crd_type_tmp = ''
        for i in range(len(tmp)):
            crd_type_tmp += tmp[i]
            if i != len(tmp)-1:
                crd_type_tmp += ' '
        self._tags['atomic_coordinate_type'] = crd_type_tmp

    def _set_uspk(self):
        self._tags['unoccupied_states_per_kpoint'] = int(self._values[0])

    def _set_positions(self):
        #print self._values
        pos_vals = self._values
        crd_type = self._tags['atomic_coordinate_type']
        positions = []
        movable = []
        pos_len = self._tags['pos_len']

        if divmod(len(pos_vals), pos_len)[1]:
            print ('Error in getting positions!\n')
            sys.exit(1)
        natom = len(pos_vals)/pos_len

        if crd_type == 'Cell Relative':
            for i in range(natom):
                positions.append([pos_vals[i*pos_len],
                                 [float(x) for x in pos_vals[i*pos_len+1:i*pos_len+4]]])
                                 #int(pos_vals[i*5+4])])
                if pos_len == 5:
                    movable.append(int(pos_vals[i*pos_len+4]))
                elif pos_len == 4:
                    #print 'Warning: Movable values NOT defined!\n'
                    movable.append(1)
        elif crd_type == 'Absolute':
            self._tags['atomic_coordinate_type'] = 'Cell Relative'
            for i in range(natom):
                positions.append([pos_vals[i*pos_len],
                                 [float(pos_vals[i*pos_len+1])/self._tags['a_length'],
                                  float(pos_vals[i*pos_len+2])/self._tags['b_length'],
                                  float(pos_vals[i*pos_len+3])/self._tags['c_length']]])
                if pos_len == 5:
                    movable.append(int(pos_vals[i*pos_len+4]))
                elif pos_len == 4:
                    #print 'Warning: Movable values NOT defined!\n'
                    movable.append(1)
        else:
            print ('Coordinate type must be either "Absolute" or')
            print ('"Cell Relative"!\n')
            print ('Your type: %s\n'%self._tags['atomic_coordinate_type'])
            sys.exit(1)

        self._tags['atoms'] = positions
        self._tags['movable'] = movable

    def _set_grid(self):
        tmp = self._values
        grid_tmp = [int(x) for x in tmp]
        self._tags['wavefunction_grid'] = grid_tmp

    def _set_kpoint_mesh(self):
        tmp = self._values
        mesh_tmp = [int(x) for x in tmp]
        self._tags['kpoint_mesh'] = mesh_tmp

    def _set_others(self):
        tmp = self._values
        others_tmp = []
        # add blank between elements
        for x in tmp:
            if x == '\n':
                others_tmp.append(x + '\n')
            else:
                others_tmp.append(x + ' ')
        self._tags['others'] = others_tmp
        #if self._tags['others'] is None:
        #    self._tags['others'] =  others_tmp
        #else:
        #    self._tags['others'] =  self._tags['others'].join(others_tmp)
        
if __name__ == '__main__':

    import sys

    #get symmetry operations
    from phonopy.structure.symmetry import Symmetry
    # abinit = PwscfIn(open(sys.argv[1]).readlines())
    cell, tags = read_rmg(sys.argv[1])
    #print cell, tags
    # symmetry = Symmetry(cell)
    # print("# %s" % symmetry.get_international_table())
    print(get_rmg_structure(cell, tags))
    #write_rmg('test.in', cell, tags)

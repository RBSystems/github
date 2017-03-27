import os
import sys

def get_relaxed_unitcell():
    # generate a unitcell from logfile and input file for RMG
    with open('rmg.in.00.log') as f:
        log_lines = f.readlines()
    
    with open('rmg.in') as f:
        inp_lines = f.readlines()
    
    # variables
    pos_flag = 0
    Ang2Bohr = 0.5291772108
    species, x, y, z, movable = [], [], [], [], []
    
    #read relaxed structure from log file
    for i in range(len(log_lines)):
        #make sure pos flag is the last one
        if 'IONIC POSITIONS' in log_lines[i]:
            for j in range(i+1, len(log_lines)):
                if 'Species' in log_lines[j]:
                    pos_flag = j
    
    for i in range(pos_flag+1, len(log_lines)):
        words = log_lines[i].split()
        species.append(words[2])
        x.append(float(words[3]))
        y.append(float(words[4]))
        z.append(float(words[5]))
        movable.append(int(words[-1]))
        if len(log_lines[i+1]) < 2:
            break
    
    
    unit_lines = '\n'
    
    for line in inp_lines:
        if "crds_units" in line:
            tmp_units = line.split('"')[1]
            break
    
    if tmp_units == "Bohr":
        factor = 1.0
    elif tmp_units == "Angstrom":
        factor = 1.0/Ang2Bohr
    else:
        print 'Units value error.\n'
        sys.exit()
    
    for line in inp_lines:
        if line.startswith('#'):
            unit_lines += line
        elif "calculation_mode" in line:
            unit_lines += 'calculation_mode="Quench Electrons"\n\n'
        elif "crds_units" in line:
            unit_lines += 'crds_units="Bohr"\n\n'
        elif "length_units" in line:
            unit_lines += 'length_units="Bohr"\n\n'
        elif "atomic_coordinate_type" in line:
            unit_lines += 'atomic_coordinate_type="Absolute"\n\n'
        elif "a_length" in line:
            a_length = float(line.split('"')[1])
            unit_lines += 'a_length="%18.12f"\n'%(a_length*factor)
        elif "b_length" in line:
            b_length = float(line.split('"')[1])
            unit_lines += 'b_length="%18.12f"\n'%(b_length*factor)
        elif "c_length" in line:
            c_length = float(line.split('"')[1])
            unit_lines += 'c_length="%18.12f"\n'%(c_length*factor)
        elif "atoms =" in line:
            unit_lines += 'atoms =\n'
            break
        else:
            unit_lines += line
    
    #unit_lines += 'atoms =\n'
    unit_lines += '"\n'
    for i in range(len(x)):
        unit_lines += '%s%12.7f%12.7f%12.7f%5d\n'%(species[i],
                                                   x[i],
                                                   y[i], 
                                                   z[i],
                                                   movable[i])
    unit_lines += '"'
    
    f = open('unitcell.in', 'wb')
    f.write(unit_lines)
    f.close()

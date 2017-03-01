import os
import sys

class RmgIn:
    def __init__(self, filename):
        self._set_methods = {'a_length': self._set_a_length,
                             'b_length': self._set_b_length,
                             'c_length': self._set_c_length,
                             'wavefunction_grid': self._set_wfc_grid,
                             'atomic_coordinate_type': self._set_crd_type,
                             'kpoint_mesh': self._set_kpt_mesh,
                             'crds_units': self._set_units,
                             'atoms': self._set_atoms,
                             'calculation_mode': self._set_calc_mode,
                             #'subdiag_driver': self._set_subdiag_driver,
                             #'relax_max_force': self._set_rlx_force,
                             #'rms_convergence_criterion': self._set_rms_conv,
                             #'occupation_type': self._set_occpations,
                             'start_mode': self._set_start_mode,
                             #'max_md_steps': self._set_md_steps,
                             #'max_scf_steps': self._set_scf_steps
        }
        self._in = {}
        self._args = {}

        self.read_file(filename)
        self._arg_parser()

    def setting_error(self, msg):
        print msg
        sys.exit(1)

    # TODO: need to find a better solution
    def read_file(self, filename):
        _in = self._in
        with open(filename, 'rb') as f:
            lines_in = f.readlines()
        for i, line in enumerate(lines_in):
            line_tmp = line.split('#')[0]
            if line_tmp == '':
                continue
            if line_tmp.find('=') != -1:
                left, right = [x.strip() for x in line_tmp.split('=')]
                left = left.lower()
                if line_tmp.count('"') == 2 or line_tmp.count("'") == 2:
                    right = right.strip('"').strip("'")
                    _in[left] = right
                elif line_tmp.count('"') == 1 or line_tmp.count("'") == 1:
                    right = right.strip('"').strip("'")
                    right_all = []
                    if right != '':
                        right_all.append(right)
                    while True:
                        i += 1
                        tmp = lines_in[i].strip().strip('"').strip("'")
                        if tmp != '':
                            right_all.append(tmp)
                        if '"' in lines_in[i] or "'" in lines_in[i]:
                            break
                    _in[left] = right_all
                elif line_tmp.count('"') == 0 or line_tmp.count("'") == 0:
                    right_all = []
                    while True:
                        i += 1
                        if '"' in lines_in[i] or "'" in lines_in[i]:
                            tmp = lines_in[i].strip().strip('"').strip("'")
                            if tmp != '':
                                right_all.append(tmp)
                            break
                    while True:
                        i += 1
                        tmp = lines_in[i].strip().strip('"').strip("'")
                        if tmp != '':
                            right_all.append(tmp)
                        if '"' in lines_in[i] or "'" in lines_in[i]:
                            break
                    _in[left] = right_all
                            
    def _arg_parser(self):
        args = self._args
        rmg_in = self._in

        for key, val in rmg_in.iteritems():
            if key in self._set_methods:
                self._set_methods[key](val)
            else:
                self._set_other(key, val)
    # TODO: need to be improved
    def _set_other(self, key, val):
        self._args[key] = val

    def _set_a_length(self, val):
        self._args['a_length'] = float(val)

    def _set_b_length(self, val):
        self._args['b_length'] = float(val)

    def _set_c_length(self, val):
        self._args['c_length'] = float(val)

    def _set_units(self, val):
        self._args['crds_units'] = str(val)

    def _set_crd_type(self, val):
        self._args['atomic_coordinate_type'] = str(val)

    def _set_wfc_grid(self, val):
        tmp = map(int, val.strip("'").split())
        self._args['wavefunction_grid'] = tmp

    def _set_kpt_mesh(self, val):
        tmp = map(int, val.strip("'").split())
        self._args['kpoint_mesh'] = tmp

    def _set_calc_mode(self, val):
        self._args['calculation_mode'] = str(val)

    def _set_atoms(self, val):
        self._args['atoms'] = str(val)

    def _set_start_mode(self, val):
        self._args['start_mode'] = str(val)

    def validate_subdiag_driver(self):
        _subdiag_driver = self._args['subdiag_driver']
        if _subdiag_driver != 'scalapack':
            print "Warning: A non-scalapck subdiag driver is used."

    def validate_pp(self):
        _pp = self._args['pseudopotential']
        for _tmp in _pp:
            element, pp_path = _tmp.split()
            if element != os.path.basename(pp_path).split('.')[0]:
                msg = "Pseudo potential doesnot match for element %s, exit."% element
                self.setting_error(msg)
            if not os.path.isfile(pp_path):
                msg = "Pseudo potential file: %s not found, exit."% pp_path
                self.setting_error(msg)

    def validate_others(self):
        pass

def validate_rmgin(args):
    args.validate_pp()
    args.validate_subdiag_driver()

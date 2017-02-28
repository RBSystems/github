class RmgIn:
    def __init__(self, filename):
        self._set_methods = {}
        self._in = {}
        self._args = {}

        self.read_file(self, filename)
        self._arg_parser()

    def read_file(self, filename):
        _in = self._in
        with open(filename, 'rb') as f:
            lines_in = f.readlines()
        for i,line in enumerate(lines_in):
            line_tmp = line.split('#')[0]
            if line_tmp == '':
                continue
            if line_tmp.find('=') != -1:
                left, right = [x.strip() for x in line_tmp.split('=')]
                left = left.lower()
                if '"' in right:
                    right = right.split('"')[1]
                elif "'" in right:
                    right = right.split("'")[1]

                if lines_tmp.count('"') == 2 or lines_tmp.count("'") == 2:
                    _in[left] = right
                else:
                    right_all = []
                    if right != '':
                        right_all.append(right)
                    while True:
                        i += 1
                        tmp = lines[i].strip().strip('"').strip("'")
                        right_all.append(tmp)
                        if '"' in tmp or "'" in tmp:
                            break
                            
    def _arg_parser(self, lines):
        pass        
def read_rmg(lines):
    pass


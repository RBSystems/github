# by default the unit is m
class length:
    def __init__(self):
        self.angstrom = 1.0e-10
        self.bohr = 5.2917721067e-11
        self.angstrom2bohr = self.get_angstrom2bohr()
        self.bohr2angstrom = self.get_bohr2angstrom()

    def get_angstrom2bohr(self):
        return self.angstrom/self.bohr

    def get_bohr2angstrom(self):
        return self.bohr/self.angstrom

class energy:
    def __init__(self):
        pass

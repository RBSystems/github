# params properties
# if param is list, then type should be [1D type, 2D type]
param_prop = {
    'nodes':     {'required': True,  'type': 'int',   'default': None},
    'time' :     {'required': True,  'type': ['list', 'int'], 'default': None},
    'exeinput':  {'required': True,  'type': 'str',   'default': None},
    'exepath':   {'required': True,  'type': 'str',   'default': None},
    'account':   {'required': True,  'type': 'str',   'default': None},
    'threads':   {'required': False, 'type': 'int',   'default': 1},
    'name':      {'required': False, 'type': 'str',   'default': 'test'},
    'queue':     {'required': False, 'type': 'str',   'default': 'debug'},
    'is_submit': {'required': False, 'type': 'bool',  'default': True},
    'force_sub': {'required': False, 'type': 'bool',  'default': False},
    'cores':     {'required': False, 'type': 'int',   'default': None},
    'exeoutput': {'required': False, 'type': 'str',   'default': None},
    'depend':    {'required': False, 'type': ['str', 'list'], 'default': [None, []]},
    'module':    {'required': False, 'type': 'str',   'default': []}
    }


# params properties
# if param is list, then type should be [1D type, 2D type]
param_prop = {
    'nodes':     {'required': True,  'type': 'int',   'default': None},
    'time' :     {'required': True,  'type': ['list', 'int'], 'default': None},
    'exeinput':  {'required': True,  'type': 'str',   'default': None},
    'exepath':   {'required': True,  'type': 'str',   'default': None},
    'threads':   {'required': False, 'type': 'int',   'default': 1},
    'name':      {'required': False, 'type': 'str',   'default': 'test'},
    'queue':     {'required': False, 'type': 'str',   'default': 'debug'},
    'is_submit': {'required': False, 'type': 'bool',  'default': True},
    'cores':     {'required': False, 'type': 'int',   'default': None},
    'exeoutput': {'required': False, 'type': 'str',   'default': None},
    'module':    {'required': False, 'type': 'str',   'default': []}
    }

# system properties
sys_prop = {
    'Cades': {'all_queues': ['batch', 'long'], 'time_threshold': 30},
    'BlueWaters': {'all_queues': ['debug', 'normal', 'high'], 'time_threshold': 30}
    }

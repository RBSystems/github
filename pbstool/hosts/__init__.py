import os
import sys

# environment variables
class InitEnv:
    def __init__(self):
        self._user = None
        self._host = None
        self._pwd  = None
        self._home_path = None

        self._set_all()

    def _set_all(self):
        self._set_user()
        self._set_host()
        self._set_pwd()
        self._set_home_path()

    def _set_user(self):
        import getpass
        self._user = getpass.getuser()

    def get_user(self):
        return self._user

    def _set_host(self):
        import socket
        hostname = socket.gethostname()
        if 'or-condo' in hostname:
            self._host = 'Cades'
        elif 'h2o' in hostname:
            self._host = 'BlueWaters'
        elif 'titan' in hostname:
            self._host = 'Titan'
        else:
            self._host = hostname
            print 'Warning: Unknown host.'

    def get_host(self):
        return self._host

    def _set_pwd(self):
        self._pwd = os.getcwd()

    def get_pwd(self):
        return self._pwd

    def _set_home_path(self):
        self._home_path = os.path.expanduser('~')

    def get_home_path(self):
        return self._home_path

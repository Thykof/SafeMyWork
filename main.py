# -*- coding: utf-8 -*-
#!/usr/bin/python3

import sys

from watcher import conf
from watcher import mod
from interface.interface import Interface

if __name__ == '__main__':
    myfile = open('stderr.log', 'a')
    sys.stderr = myfile
    config = conf.get_config()
    root = Interface(config)
    root.run()

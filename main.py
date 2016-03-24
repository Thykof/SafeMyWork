# -*- coding: utf-8 -*-
#!/usr/bin/python3

import sys

from watcher import conf
from interface.interface import Interface

myfile = open('stderr.log', 'a')
sys.stderr = myfile

if __name__ == '__main__':
    config = conf.get_config()
    root = Interface(config)
    root.run()

# -*- coding: utf-8 -*-
#!/usr/bin/python3

import atexit
import sys

from watcher import conf
from watcher import mod
from watcher.watcher import Watcher
from interface.interface import Interface

def quit_(config):
    mod.tell('Save config')
    conf.save_config(config)

if __name__ == '__main__':
    myfile = open('stderr.log', 'a')
    sys.stderr = myfile

    config = conf.get_config()
    if config is None:
        mod.tell('No delicate directory')
        mod.tell('Save config')
        sys.exit()
    atexit.register(quit_, config)
    watcher = Watcher(config)
    root = Interface()
    root.set_watcher(watcher)
    root.run()

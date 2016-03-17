# -*- coding: utf-8 -*-

import atexit
from os import system
import sys

from smw_core import conf
from smw_core import mod
from smw_core.watcher import Watcher

def quit_(config):
    mod.tell('Save config')
    conf.save_config(config)
    system('pause')

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
    watcher.start()

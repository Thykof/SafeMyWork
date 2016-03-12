# -*- coding: utf-8 -*-

import atexit
from os import system

from smw_core import mod
from smw_core import conf
from smw_core.watcher import Watcher

def quit(config):
    conf.save_config(config)
    system('pause')

if __name__ == '__main__':
    config = conf.get_config()
    atexit.register(quit, config)
    watcher = Watcher(config)
    watcher.start()

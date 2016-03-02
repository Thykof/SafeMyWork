# -*- coding: utf-8 -*-

import os

from sample import mod
from sample import conf
from sample.watcher import Watcher

if __name__ == '__main__':
    DIR = mod.get_dir()
    try:
        config = conf.read_config()
    except FileNotFoundError:
        conf.save_config()  # Initialize config
        config = conf.read_config()
    watcher = Watcher(DIR, config)
    watcher.start()

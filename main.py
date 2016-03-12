# -*- coding: utf-8 -*-

import atexit

from smw_core import mod
from smw_core import conf
from smw_core.watcher import Watcher

if __name__ == '__main__':
    config = conf.get_config()
    atexit.register(conf.save_config, config)
    watcher = Watcher(config)
    watcher.start()

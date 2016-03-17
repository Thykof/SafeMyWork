# -*- coding: utf-8 -*-

import atexit
import sys

from smw_core import conf
from smw_core.watcher import Watcher

if __name__ == '__main__':
    myfile = open('stderr.log', 'a')
    sys.stderr = myfile

    config = conf.get_config()
    atexit.register(conf.save_config, config)
    watcher = Watcher(config)
    watcher.start()

# -*- coding: utf-8 -*-

from smw_core import mod
from smw_core import conf
from smw_core.watcher import Watcher

if __name__ == '__main__':
    delicate_dir = mod.get_dir()
    try:
        config = conf.read_config()
    except FileNotFoundError:
        conf.save_config()  # Initialize config
        config = conf.read_config()
    mod.create_archive_dir(config['archive_dir'], delicate_dir)
    watcher = Watcher(delicate_dir, config)
    watcher.start()

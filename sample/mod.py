# -*- coding: utf-8 -*-

import sys

def tell(message):
    """Tell to user a message"""
    print(message)

def get_dir():
    """Return dir to watch."""
    if len(sys.argv) > 2:
        mod.tell('Only one dir please.')
        sys.exit()
    else:
        directory = sys.argv[1]
    return directory

# -*- coding: utf-8 -*-

"""Define some fonctions."""

import sys
from os import path, mkdir

def tell(message):
    """Tell to user a message."""
    print(message)

def get_dir():
    """Return dir to watch."""
    if len(sys.argv) == 1:
        tell('Please give a directory to watch.')
        sys.exit()
    else:
        return sys.argv[1:]

def combine_list(list1, list2):
    """Return a list with only the element in the two lists."""
    list3 = list()
    for value in list1:
        if value in list2:
            list3.append(value)
    return list3

def create_archive_dir(archive_dir, delicate_dir):
    if not path.exists(archive_dir):
        mkdir(archive_dir)
    for directory in delicate_dir:
        if not path.exists(path.join(archive_dir, directory)):
            mkdir(path.join(archive_dir, directory))

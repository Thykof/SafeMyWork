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
    elif len(sys.argv) > 2:
        tell('Only one dir please.')
        sys.exit()
    else:
        directory = sys.argv[1]
    return directory

def combine_list(list1, list2):
    """Return a list with only the element in the two lists."""
    list3 = list()
    for value in list1:
        if value in list2:
            list3.append(value)
    return list3

def create_archive_dir(archive_dir):
    if not path.exists(archive_dir):
        mkdir(archive_dir)

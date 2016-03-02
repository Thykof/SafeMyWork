# -*- coding: utf-8 -*-

import sys

def tell(message):
    """Tell to user a message."""
    print(message)

def get_dir():
    """Return dir to watch."""
    if len(sys.argv) > 2:
        mod.tell('Only one dir please.')
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

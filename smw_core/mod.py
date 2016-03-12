# -*- coding: utf-8 -*-

"""Define some fonctions."""

from os import path, mkdir

def tell(message):
    """Tell to user a message."""
    print(message)
    with open('output.log', 'a') as myfile:
        myfile.write(message + '\n')

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
        dir_to_create = path.join(archive_dir, path.basename(directory))
        if not path.exists(dir_to_create):
            mkdir(dir_to_create)

# -*- coding: utf-8 -*-

"""Define some fonctions."""

from os import path, mkdir

def tell(message, target='output.log'):
    """Tell to user a message.

    :func:`print` the message and write it in *output.log* file.

    :param message: the message
    :type message: ``str``
    :param target: The file, default to *output.log*
    :type target: ``str``
    """
    print(message)
    with open(target, 'a') as myfile:
        myfile.write(message + '\n')

def combine_list(list1, list2):
    """Create a list with only elements in common of the two lists.

    :param list1: the first list
    :type list1: ``list``
    :param list2: the second list
    :type list2: ``list``
    :returns: the created list
    :rtype: ``list``
    """
    list3 = list()
    for value in list1:
        if value in list2:
            list3.append(value)
    return list3

def create_archive_dir(archive_dir, delicate_dir):
    """Create all directories use for archiving.

    :param archive_dir: the archive directory
    :type archive_dir: ``str``
    :param delicate_dir: directories to watch
    :type delicate_dir: ``list``
    """
    if not path.exists(archive_dir):
        mkdir(archive_dir)
    for directory in delicate_dir:
        dir_to_create = path.join(archive_dir, path.basename(directory))
        if not path.exists(dir_to_create):
            mkdir(dir_to_create)

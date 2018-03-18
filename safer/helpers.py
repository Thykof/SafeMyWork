#!/usr/bin/python3

"""Define some fonctions."""

from os import path as ospath, listdir
import json

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

def path_without_root(path):
	"""Return the `path` without the first directory.

	e.g. "root/foo/bar" -> "foo/bar"

	"""
	pos = path.find('/')  # attention: conpatibility on win!
	if pos != -1:
		return path[pos+1:]
	else:
		return ''

def missing_item(list1, list2):
	"""Return the list of directory in `list1` but not in `list2`."""
	result = list()
	for item in list1:
		if item not in list2:
			result.append(item)
	return result

def split_path(path):
	"""Return a list with all direcotry name in the given path."""
	dirs = list()  # Result
	stop = False
	while not stop:
		dirname = ospath.basename(path)
		if dirname != '':
			dirs.append(dirname)
		else:
			stop = True
		path = ospath.dirname(path)

	return dirs

def store(content, pathdir, filename):
    json_file = ospath.join(pathdir, filename)
    with open(json_file, 'w', encoding='utf-8') as myfile:
        myfile.write(json.dumps(content, indent=2))

def get_folder_size(folder):
    total_size = ospath.getsize(folder)
    for item in listdir(folder):
        itempath = ospath.join(folder, item)
        if ospath.isfile(itempath):
            total_size += ospath.getsize(itempath)
        elif ospath.isdir(itempath):
            total_size += get_folder_size(itempath)
    return total_size

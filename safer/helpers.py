#!/usr/bin/python3

"""Define some functions."""

from os import path, listdir, mkdir
from sys import exit
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

def path_without_root(path_):
	"""Return the `path` without the first directory.

	e.g. "root/foo/bar" -> "foo/bar"

	"""
	dirs = split_path(path_)
	if len(dirs) <= 1:
		return ''
	dirs.reverse()
	res = dirs[1]
	if len(dirs) == 2:
		return res
	i = 2
	while i < len(dirs):
		res = path.join(res, dirs[i])
		i += 1
	return res

def missing_item(list1, list2):
	"""Return the list of directories in `list1` but not in `list2`."""
	result = list()
	for item in list1:
		if item not in list2:
			result.append(item)
	return result

def split_path(path_):
	"""Return a list with all directory names in the given path."""
	dirs = list()  # Result
	stop = False
	while not stop:
		dirname = path.basename(path_)
		if dirname != '':
			dirs.append(dirname)
		else:
			stop = True
		path_ = path.dirname(path_)

	return dirs

def store(content, pathdir, filename):
	json_file = path.join(pathdir, filename)
	with open(json_file, 'w', encoding='utf-8') as myfile:
		myfile.write(json.dumps(content, indent=2))

def get_folder_size(folder):
	total_size = path.getsize(folder)
	for item in listdir(folder):
		itempath = path.join(folder, item)
		if path.isfile(itempath):
			total_size += path.getsize(itempath)
		elif path.isdir(itempath):
			total_size += get_folder_size(itempath)
	return total_size

def create_dir(name, logger=None):
	try:
		mkdir(name)
	except OSError as e:
		if logger:
			logger.error(str(e))
		else:
			print(str(e))
		exit()

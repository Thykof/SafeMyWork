# -*- coding: utf-8 -*-
#!/usr/bin/python3

"""Define some fonctions."""

from os import path, mkdir

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

def path_without_root(old_path):
	pos = old_path.find('/')  # attention: conpatibility on win!
	if pos != -1:
		return old_path[pos+1:]
	else:
		return ''

def missing_item(list1, list2):
	"""Return the list of directory in list1 but not in list2."""
	result = list()
	for item in list1:
		if item not in list2:
			result.append(item)
	return result

# -*- coding: utf-8 -*-
#!/usr/bin/python3

from shutil import copytree
from os import path, listdir, mkdir

class Safer(object):
	"""Manage the creation of the duplicate directory of the folder placed under supervision."""
	def __init__(self, delicate_dirs, destination):
		super(Safer, self).__init__()
		self.delicate_dirs = delicate_dirs # List of different directories placed under supervision
		self.destination = destination
		if not path.exists(self.destination):
			mkdir(self.destination)
	
	def start(self):
		for directory in self.delicate_dirs: # Save files from all delicate directories
			root_destination = path.join(self.destination, directory)
			if not path.exists(root_destination):
				mkdir(path.join(self.destination, directory))
			list_version = list()
			for directory_version in listdir(root_destination):
				list_version.append(int(directory_version.split('V--')[1]))
			if list_version == []:
				version = '1'
			else:
				version = str(max(list_version) + 1)
			destination = path.join(self.destination, directory, directory + 'V--' + version)
			copytree(directory, destination)
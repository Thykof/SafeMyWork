#!/usr/bin/python3

from shutil import copytree, copy2
import logging
from logging.handlers import RotatingFileHandler
from os import path, listdir, mkdir, walk

class Safer(object):
	"""Manage the creation of the duplicate directory of the folder placed under supervision.

	Filename, folder, path to folder and extension can be exclude.

	"""
	# Destination folder: make in __init__
	# Delicate folders in destination: make in get_destination, call in __init__
	# Folder of version and delicate folder in version folder: make in start

	def __init__(self, delicate_dirs=list(), destination=str(), config=dict()):
		""""delicate_dirs: list of different directories placed under supervision."""
		super(Safer, self).__init__()
		# Set destination directories
		self.destination = destination
		# Make destination directories
		if not path.exists(self.destination):
			mkdir(self.destination)
		self.safe_dirs = self.get_destination(delicate_dirs)  

		# Logging
		self.logger = logging.getLogger()
		self.logger.setLevel(logging.DEBUG)
		# Log in a file
		file_handler = RotatingFileHandler('activity.log', 'a', 1000000, 1)
		file_handler.setLevel(logging.DEBUG)
		formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
		file_handler.setFormatter(formatter)
		self.logger.addHandler(file_handler)
		# Log in the console
		steam_handler = logging.StreamHandler()
		steam_handler.setLevel(logging.DEBUG)
		self.logger.addHandler(steam_handler)

		# Config
		self.exclude_filename = []
		self.exclude_dirname = []  # All folder-name in this list are exclude
		self.exclude_dirpath = []  # specific path to a folder to exclude; full path to a folder to exclude
		self.exclude_ext = []  # '' mean a file without extension
		# TODO: get config from a file (cammand line), or give them in arg (interface)

	def get_destination(self, delicate_dirs):
		"""Create a dict with folder under supervision as key and the path to their safe destination with their version."""
		safe_dirs = dict()
		for dirname in delicate_dirs:
			# Make safe directory for each delicate folder
			root_destination = path.join(self.destination, dirname)  # e.g. delicate_dir/my_work
			if not path.exists(root_destination):
				mkdir(root_destination)
			# Get version
			version = self.get_version(root_destination)
			# Add the safe directory
			safe_dirs[dirname] = path.join(self.destination, dirname, dirname + 'V--' + version)
		return safe_dirs

	def get_version(self, root_destination):
		"""Return the current version of the given safe directory."""
		list_version = list()
		for directory_version in listdir(root_destination):  # e.g. safe_dir/my_wirkV--n
			dir_splited = directory_version.split('V--')
			if len(dir_splited) == 2:
				list_version.append(int(dir_splited[1]))
		if list_version == []:
			version = '1'
		else:
			version = str(max(list_version) + 1)  # Take the last version + 1
		return version

	def start(self):
		"""Save all folder under supervision.

		It create the directories requires.
		It don't save the files that don't match with the exclusion rules.

		"""
		self.logger.info(str(self.safe_dirs))
		self.logger.info('start saving')
		self.stop_ = False
		self.logger.info('saving')
		for dirname, safe_path in self.safe_dirs.items():
			mkdir(safe_path)
			to_save, dir_to_make = self.get_to_save(dirname)
			for dirname in dir_to_make:
				mkdir(path.join(safe_path, dirname))
			self.save_files(to_save, safe_path)
		self.logger.info('end of saving')

	def get_to_save(self, directory):
		"""Return a list of file to save from a the given delicate directory, using walk.

		It make this list depending on exclusion rules.

		"""
		list_files = list()  # list of relatif path to each file
		dir_to_make = list()  # lis of directory to make in the safe root directory
		for dirpath, dirnames, filenames in walk(directory):  # walk() return a generator
			# dirpath = directory, for the first time
			# dirpath = subdirs of directory
			if path.basename(dirpath) in self.exclude_dirname:
				break
			pos = dirpath.find('/')  # attention: conpatibility on win!
			dirname = dirpath[pos+1:]
			# Exclude a path
			if dirname not in self.exclude_dirpath:
				dir_to_make.append(dirpath)
				for filename in filenames:
					# Find the extension
					ext = path.splitext(filename)[1][1:]
					if filename not in self.exclude_filename and ext not in self.exclude_ext:
						list_files.append(path.join(dirpath, filename))
		return list_files, dir_to_make

	def save_files(self, to_save, safe_path):
		for filename in to_save:
			dst = path.join(safe_path, filename)
			self.logger.info('coping: '+ dst)
			copy2(filename, dst)


	def save_dirs(self):
		"""Save all files from all delicate directories.

		Do the same that self.start without any filter.

		"""
		for dirname, safe_path in self.safe_dirs.items():
			root_safe_path = path.split(safe_path)[0]
			new_safe_path = path.join(root_safe_path, dirname + 'COPY')
			copytree(dirname, safe_path)

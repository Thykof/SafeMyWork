#!/usr/bin/python3

from shutil import copytree, copy2, rmtree
import logging
from logging.handlers import RotatingFileHandler
from os import path, listdir, mkdir, walk, remove, stat, chdir
from yaml import load, dump


from .mod import combine_list, path_without_root, missing_item

"""TODO: file log in safe_doc/folder."""


class Safer(object):
	"""Manage the creation of the duplicate directory of the folder placed under supervision.

	Filename, folder, path to folder and extension can be exclude.

	Usage:
	safer.save()  # Copy with filters rules
	safer.save(_filter=False)  # Copy the entire directories
	safer.update()  # Make a copy and update it

	"""
	# Destination folder: make in __init__
	# Delicate folders in destination: make in get_dst_path, call in __init__
	# Folder of version and delicate folder in version folder: make in save

	def __init__(self, delicate_dirs=None, destination=None, config=None):
		"""Manage logging, make destination directory, manage destinations, manage config"""
		# delicate_dirs: list of different directories placed under supervision
		super(Safer, self).__init__()
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
		self.cfg_dir = path.join(path.expanduser('~'), '.safemywork')
		self.cfg_file = path.join(self.cfg_dir, 'config.yml')
		if config is None:
			self.get_config(delicate_dirs, destination)
		else:
			self.config = config
			if config['safe_dir'] is None:
				self.destination = path.join(path.expanduser('~'), 'safe_docs')
			else:
				self.destination = config['safe_dir']
			self.delicate_dirs = config['delicate_dirs']
			self.save_config()

		self.safe_dirs = self.get_dst_path()

	def get_config(self, delicate_dirs, destination):
		if path.exists(self.cfg_file):
			self.logger.info('Read config file')
			with open(self.cfg_file, 'r') as ymlfile:
				self.config = load(ymlfile)
			if destination is None:
				self.destination = self.config['safe_dir']
			else:
				self.destination = destination
			if delicate_dirs is None:
				self.delicate_dirs = self.config['delicate_dirs']
			else:
				self.delicate_dirs = delicate_dirs
		else:
			if destination is None:
				self.destination = path.join(path.expanduser('~'), 'safe_docs')
			if delicate_dirs is None:
				self.delicate_dirs = []

			self.config = {
				'dirname': [],
				'dirpath': [],
				'filename': [],
				'extention': []
				}
			self.save_config()

	def save_config(self):
		self.config['safe_dir'] = self.destination
		self.config['delicate_dirs'] = self.delicate_dirs
		self.logger.info('Write config file')
		if not path.exists(self.cfg_dir):
			self.logger.info('Make directory: ' + self.cfg_dir)
			mkdir(self.cfg_dir)
		with open(self.cfg_file, 'w') as ymlfile:
			dump(self.config, ymlfile)

	def set_destination(self, destination):
		self.destination = destination
		self.safe_dirs = self.get_dst_path()
		print(self.safe_dirs)

	def set_delicate_dirs(self, delicate_dirs):
		self.delicate_dirs = delicate_dirs
		self.safe_dirs = self.get_dst_path()

	def add_delicate_dir(self, delicate_dir):
		self.delicate_dirs.append(delicate_dir)
		self.safe_dirs = self.get_dst_path()

	def del_delicate_dir(self, delicate_dir):
		try:
			self.delicate_dirs.remove(delicate_dir)
		except ValueError:
			pass
		self.safe_dirs = self.get_dst_path()

	def get_dst_path(self):
		"""Create a dict with folder under supervision as key and the path to their safe destination with their version.

		Three path for each folder: update, copy with filter and without.

		"""
		# Make destination directories
		if not path.exists(self.destination):
			self.logger.info('Make directory: ' + self.destination)
			mkdir(self.destination)  # e.g. safe_docs

		safe_dirs = dict()
		for path_delicate in self.delicate_dirs:
			safe_dirname = path.basename(path_delicate)
			# Make safe directory for each delicate folder
			root_destination = path.join(self.destination, safe_dirname)  # e.g. delicate_dir/my_work
			if not path.exists(root_destination):
				self.logger.info('Make directory: ' + root_destination)
				mkdir(root_destination)  # e.g. safe_docs/my_work
			# Get versions
			version_copy = self.get_version(root_destination, 'COPY')
			version_filter = self.get_version(root_destination)
			# Add the safe directories
			dst = path.join(self.destination, safe_dirname, safe_dirname + 'UPTODATE')
			dst_copy = path.join(self.destination, safe_dirname, safe_dirname + 'COPY-' + version_copy)
			dst_filter = path.join(self.destination, safe_dirname, safe_dirname + 'FILTER-' + version_filter)

			destination = {'LAST': dst, 'COPY': dst_copy, 'FILTER': dst_filter}
			safe_dirs[path_delicate] = destination
		return safe_dirs

	def get_version(self, root_destination, _type='FILTER'):
		"""Return the current version of the given safe directory.

		_type is 'FILTER' (default) or 'COPY'

		"""
		list_version = list()
		for directory_version in listdir(root_destination):
			dir_splited = directory_version.split(_type + '-')
			if len(dir_splited) == 2:
				list_version.append(int(dir_splited[1]))

		if list_version == []:
			version = '1'
		else:
			version = str(max(list_version) + 1)  # Take the last version + 1
		return version

	def save(self, _filter=True):
		"""Save all folder under supervision.

		It make a new version of safe directory
		It create the directories requires.
		If _filter is False (default), it don't save the files that don't match with the exclusion rules.

		"""
		if _filter:
			self.logger.info('Start saving with filters')
			for path_delicate, safe_path in self.safe_dirs.items():
				self.logger.info(path_delicate)
				self.logger.info('Make directory: ' + safe_path['FILTER'])
				mkdir(safe_path['FILTER'])  # e.g. safe_docs/my_work/my_workV--n
				to_save, dirs_to_make = self.get_to_save(path_delicate)

				for path_delicate in dirs_to_make:
					path_delicate = path_without_root(path_delicate)
					self.logger.info('Make directory: ' + path.join(safe_path['FILTER'], path_delicate))
					mkdir(path.join(safe_path['FILTER'], path_delicate))  # e.g. safe_docs/my_work/my_workV--n/folder
				self.save_files(to_save, safe_path['FILTER'], path_delicate)
		else:
			self.logger.info('Start copying')
			for path_delicate, safe_path in self.safe_dirs.items():
				self.logger.info('Saving ' + path_delicate)
				copytree(path_delicate, safe_path['COPY'])
		self.logger.info('Done')

	def update(self):
		"""Update the safe directory.

		It create the directories requires and consider filtration rules.
		Copy the new files, remove the old ones.
		Remove directories trees is necessary.

		"""
		self.logger.info('Start updating')
		for path_delicate, safe_path in self.safe_dirs.items():
			self.logger.info(path_delicate)
			safe_path_last = safe_path['LAST']
			if not path.exists(safe_path_last):
				self.logger.info('Make directory: ' + safe_path_last)
				mkdir(safe_path_last)  # e.g. safe_docs/my_work/my_workUPTODATE


			to_save, dirs_to_save = self.get_to_save(path_delicate)  # List delicate files
			saved, dirs_maked = self.get_saved(safe_path_last)  # List saved files

			# Make new folders
			# dirs_to_make: new directories, not yet copying
			dirs_to_make = missing_item(dirs_to_save, dirs_maked)
			for dirname in dirs_to_make:
				self.logger.info('Make directory: ' + path.join(safe_path_last, dirname))
				mkdir(path.join(safe_path_last, dirname))  # e.g. safe_docs/my_work/my_workV--n/folder

			# Copy new files
			to_copy = missing_item(to_save, saved)
			self.save_files(to_copy, safe_path_last, path_delicate)

			# Update existing files in safe path
			to_update = combine_list(to_save, saved)
			self.update_files(to_update, safe_path_last, path_delicate)

			# Remove old files
			to_del = missing_item(saved, to_save)
			self.remove_files(to_del, safe_path_last)

			# Delete old folders
			# dirs_to_del: directories copied, deleted in delicate drectory -> to delete from safe directory
			# Remove the directory tree
			dirs_to_del = missing_item(dirs_maked, dirs_to_save)
			for dirname in dirs_to_del:
				self.logger.info('Remove tree: ' + path.join(safe_path_last, dirname))
				try:
					rmtree(path.join(safe_path_last, dirname))
				except FileNotFoundError:
					pass  # Directory already removed

		self.logger.info('Done')

	def get_to_save(self, directory):
		"""Return a list of file to save from a the given delicate directory, using walk.

		It make this list depending on exclusion rules.

		"""
		list_files = list()  # List of relatif path to each file
		dirs_to_make = list()  # List of directory to make in the safe root directory
		chdir(path.dirname(directory))
		directory = path.basename(directory)
		for dirpath, dirnames, filenames in walk(directory):  # walk() return a generator
			# dirpath = directory, for the first time
			# dirpath = subdirs of directory
			# Exclude a directory name
			if path.basename(dirpath) in self.config['dirname']:
				continue
			dirname = path_without_root(dirpath)
			# Exclude a path
			if dirname not in self.config['dirpath']:
				if path.basename(dirpath) != directory:
					dirs_to_make.append(dirname)
				for filename in filenames:
					# Find the extension
					ext = path.splitext(filename)[1][1:]
					if filename not in self.config['filename'] and ext not in self.config['extention']:
						list_files.append(path.join(dirname, filename))

		return list_files, dirs_to_make

	def get_saved(self, directory):
		"""Return the files and the folders in the safe path."""
		saved = list()  # List of relatif path to each file
		dirs_maked = list()  # List of directory to make in the safe root directory

		chdir(path.dirname(directory))  # .../safe_docs/folder
		directory = path.basename(directory)  # folderUPTODATE
		for dirpath, dirnames, filenames in walk(directory):  # walk() return a generator
			# dirpath = directory, for the first time
			# dirpath = subdirs of directory
			dirname = path_without_root(dirpath)
			if 'UPTODATE' not in dirname and dirname != '':
				dirs_maked.append(dirname)
			for filename in filenames:
				saved.append(path.join(dirname, filename))
		return saved, dirs_maked

	def save_files(self, to_save, safe_path, path_delicate):
		"""Copy the files in to_save in the safe_path."""
		for filename in to_save:
			dst = path.join(safe_path, filename)
			self.logger.info('Copy: '+ dst)
			copy2(path.join(path_delicate, filename), dst)

	def update_files(self, to_update, safe_path, path_delicate):
		"""Update the files in to_update."""
		for file_path in to_update:
			src = path.join(path_delicate, file_path)
			dst = path.join(safe_path, file_path)
			if self.compare_file(src, dst):
				self.logger.info('Update: '+ file_path)
				with open(src, 'rb') as myfile:
					content = myfile.read()
				with open(dst, 'wb') as myfile:
					myfile.write(content)

	def remove_files(self, to_del, safe_path_last):
		"""Remove the files in to_del."""
		for filename in to_del:
			target = path.join(safe_path_last, filename)
			self.logger.info('Remove: ' + target)
			remove(target)

	def compare_file(self, file1, file2):
		"""Return True if file1 is most recent one."""
		stat_file1 = stat(file1)
		stat_file2 = stat(file2)
		return stat_file1.st_mtime > stat_file2.st_mtime

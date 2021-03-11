#!/usr/bin/python3

import asyncio
from shutil import copytree, copy2, rmtree, Error
import logging
from logging.handlers import RotatingFileHandler
from os import path, listdir, walk, remove, chdir
from json import load, dump
import json


from safer import helpers as h

MAX_DIR_SIZE = 3000000000

class Safer:
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
		file_handler = RotatingFileHandler('activity.log', maxBytes=1000000, backupCount=50, encoding='utf-8')
		file_handler.setLevel(logging.DEBUG)
		formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
		file_handler.setFormatter(formatter)
		self.logger.addHandler(file_handler)
		# Log in the console
		stream_handler = logging.StreamHandler()
		stream_handler.setLevel(logging.INFO)
		self.logger.addHandler(stream_handler)

		# Config
		self.cfg_dir = path.join(path.expanduser('~'), '.safemywork')
		self.cfg_file = path.join(self.cfg_dir, 'config.json')
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

		self.stop = False

		self.safe_dirs = self.get_dst_path()

	def get_config(self, delicate_dirs, destination):
		if path.exists(self.cfg_file):
			self.logger.info('Read config file')
			with open(self.cfg_file, 'r') as json_file:
				self.config = load(json_file)
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
				'extention': [],
				'local_path': '',
				'external_path': '',
				'timedelta': 1,
				'advanced': False
			}
			self.save_config()

	def save_config(self):
		"""
		:param new_itmes: other data to save (timedelta)
		:type new_items: ``dict``
		"""
		self.config['safe_dir'] = self.destination
		self.config['delicate_dirs'] = self.delicate_dirs
		self.logger.info('Write config file')
		if not path.exists(self.cfg_dir):
			self.logger.debug('Make directory: ' + self.cfg_dir)
			h.create_dir(self.cfg_dir, self.logger)
		with open(self.cfg_file, 'w') as json_file:
			dump(self.config, json_file)

	def set_destination(self, destination):
		self.destination = destination
		self.safe_dirs = self.get_dst_path()

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
			self.logger.error('ERROR: del delicate dir, ValueError, safer')
		self.safe_dirs = self.get_dst_path()

	def get_dst_path(self):
		"""Create a dict with folder under supervision as key and the path to their safe destination with their version.

		Three path for each folder: update, copy with filter and without.

		"""
		# Make destination directories
		if not path.exists(self.destination):
			self.logger.debug('Make directory: ' + self.destination)
			h.create_dir(self.destination, self.logger)  # e.g. safe_docs

		safe_dirs = dict()
		for path_delicate in self.delicate_dirs:
			safe_dirname = path.basename(path_delicate)
			# Make safe directory for each delicate folder
			root_destination = path.join(self.destination, safe_dirname)  # e.g. delicate_dir/my_work
			if not path.exists(root_destination):
				self.logger.debug('Make directory: ' + root_destination)
				h.create_dir(root_destination, self.logger)  # e.g. safe_docs/my_work
			# Get versions
			version_copy = self.get_version(root_destination, 'COPY')
			version_filter = self.get_version(root_destination)
			# Add the safe directories
			dst = path.join(self.destination, safe_dirname, safe_dirname + 'UPTODATE')
			dst_copy = path.join(self.destination, safe_dirname, safe_dirname + 'COPY-' + version_copy)
			dst_filter = path.join(self.destination, safe_dirname, safe_dirname + 'FILTER-' + version_filter)
			dst_sync = path.join(self.destination, safe_dirname, safe_dirname + 'SYNC')

			destination = {'LAST': dst, 'COPY': dst_copy, 'FILTER': dst_filter, 'SYNC':dst_sync, 'activate': True}
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

	def save_with_filters(self, loop=None):
		"""Save all folder under supervision.

		It make a new version of safe directory
		It create the directories requires.

		"""
		error = list()  # limit size
		errors = list()  # file not found
		self.logger.info('Start saving with filters')
		for path_delicate, safe_path in self.safe_dirs.items():
			if not path.exists(path_delicate):
				break
			if h.get_folder_size(path_delicate) > MAX_DIR_SIZE and not self.config['advanced']:
				error.append(path_delicate)
				continue
			if safe_path['activate']:
				safe_path_filter = safe_path['FILTER']
				self.logger.debug(path_delicate)
				self.logger.debug('Make directory: ' + safe_path_filter)
				h.create_dir(safe_path_filter, self.logger)  # e.g. safe_docs/my_work/my_workV--n

				if loop is None:
					loop = asyncio.get_event_loop()
				loop.run_until_complete(self.get_to_save(path_delicate))

				dirs_to_make = self.dirs_to_make
				to_save = self.list_files

				for dirname in dirs_to_make:
					#dirname = h.path_without_root(dirname)
					dirpath = path.join(safe_path_filter, dirname)
					self.logger.debug('Make directory: ' + dirpath)
					if not path.exists(dirpath):
						h.create_dir(dirpath, self.logger)  # e.g. safe_docs/my_work/my_workV--n/folder
				errors.extend(self.save_files(to_save, safe_path_filter, path_delicate))

		self.logger.info('Done')
		self.safe_dirs = self.get_dst_path()
		return error, errors

	def copy_files(self):
		error = list()
		self.logger.info('Start copying')
		for path_delicate, safe_path in self.safe_dirs.items():
			if not path.exists(path_delicate):
				break
			if safe_path['activate']:
				size = h.get_folder_size(path_delicate)
				if size > MAX_DIR_SIZE and not self.config['advanced']:
					self.logger.warning('Limit size reached, abort')
					error.append(path_delicate)
				else:
					self.logger.info('Saving ' + path_delicate)
					try:
						copytree(path_delicate, safe_path['COPY'])
					except Error as e:
						error.append(str(e))
						self.logger.error(str(e))

		self.logger.info('Done')
		self.safe_dirs = self.get_dst_path()
		return error, list()

	def update(self, loop=None):
		"""Update the safe directory.

		It create the directories requires and consider filtration rules.
		Copy the new files, remove the old ones.
		Remove directories trees is necessary.

		"""
		error = list()  # limit size
		errors = list()  # File not found
		self.logger.info('Start updating')
		for path_delicate, safe_path in self.safe_dirs.items():
			if not path.exists(path_delicate):
				break
			if h.get_folder_size(path_delicate) > MAX_DIR_SIZE and not self.config['advanced']:
				error.append(path_delicate)
				continue
			if safe_path['activate']:
				self.logger.info(path_delicate)
				safe_path_last = safe_path['LAST']
				if not path.exists(safe_path_last):
					self.logger.debug('Make directory: ' + safe_path_last)
					h.create_dir(safe_path_last, self.logger)  # e.g. safe_docs/my_work/my_workUPTODATE

				if loop is None:
					loop = asyncio.get_event_loop()
				loop.run_until_complete(asyncio.wait([self.get_to_save(path_delicate), self.get_saved(safe_path_last),], loop=loop))

				dirs_to_save, dirs_maked = self.dirs_to_make, self.dirs_maked
				to_save, saved = self.list_files, self.saved

				# Make new folders
				# dirs_to_make: new directories, not yet copying
				dirs_to_make = h.missing_item(dirs_to_save, dirs_maked)
				for dirname in dirs_to_make:
					directory_to_create = path.join(safe_path_last, dirname)
					self.logger.debug('Make directory: ' + directory_to_create)
					h.create_dir(directory_to_create, self.logger)

				# Copy new files
				to_copy = h.missing_item(to_save, saved)
				errors.extend(self.save_files(to_copy, safe_path_last, path_delicate))

				# Update existing files in safe path
				to_update = h.combine_list(to_save, saved)
				errors.extend(self.update_files(to_update, safe_path_last, path_delicate))

				# Remove old files
				to_del = h.missing_item(saved, to_save)
				errors.extend(self.remove_files(to_del, safe_path_last))

				# Delete old folders
				# dirs_to_del: directories copied, deleted in delicate drectory -> to delete from safe directory
				# Remove the directory tree
				dirs_to_del = h.missing_item(dirs_maked, dirs_to_save)
				for dirname in dirs_to_del:
					self.logger.info('Remove tree: ' + path.join(safe_path_last, dirname))
					try:
						rmtree(path.join(safe_path_last, dirname))
					except FileNotFoundError:
						pass  # Directory already removed

		self.logger.info('Done')
		self.safe_dirs = self.get_dst_path()  # !!! probleme avec activate
		return error, errors

	async def get_to_save(self, directory):
		"""Return a list of file to save from a the given delicate directory, using `os.walk`.

		It make this list depending on exclusion rules.

		"""
		list_files = list()  # List of relatif path to each file
		dirs_to_make = list()  # List of directory to make in the safe root directory
		chdir(path.dirname(directory))
		directory_walk = path.basename(directory)
		for dirpath, _, filenames in walk(directory_walk):  # walk() return a generator
			# dirpath = directory, for the first time
			if self.stop:
				break
			self.logger.info(dirpath)

			# Exclude a directory name
			can = True
			for dirname in h.split_path(dirpath):
				if dirname in self.config['dirname']:
					can = False
			if not can:
				self.logger.info('Skip dirname: ' + dirpath)
				continue

			# Exclude a path
			can = True
			for dirname in self.config['dirpath']:
				if dirpath.find(dirname) != -1 and dirname != '':
					can = False

			if can:
				dirname = h.path_without_root(dirpath)
				if dirpath != directory_walk:  # Exclude root path
					dirs_to_make.append(dirname)
				else:
					self.logger.info('Skip root dir: ' + dirpath)

				# Take all files (even in the root directory)
				for filename in filenames:
					# Find the extension
					ext = path.splitext(filename)[1][1:]
					if filename not in self.config['filename'] and ext not in self.config['extention']:
						list_files.append(path.join(dirname, filename))
					else:
						self.logger.info('Skip filename or extention:' + path.join(dirname, filename))
					if self.stop:
						break
			else:
				self.logger.info('Skip dirpath: ' + dirpath)

		self.list_files = list_files
		self.dirs_to_make = dirs_to_make
		results = dict()
		results['list_files'] = list_files
		results['dirs_to_make'] = dirs_to_make

		json_filename = 'analysisW' + '_'.join(directory.replace('\\', '/').split('/')) + '.json'
		json_file = path.join(self.destination, json_filename)
		self.logger.info('Store analysis: ' + json_file)
		with open(json_file, 'w', encoding='utf-8') as myfile:
			myfile.write(json.dumps(results, indent=2))


	async def get_saved(self, directory):
		"""Return the files and the folders in the safe path (files already saved), using `os.walk`."""
		saved = list()  # List of relatif path to each file
		dirs_maked = list()  # List of directory to make in the safe root directory

		chdir(path.dirname(directory))  # .../safe_docs/folder
		directory = path.basename(directory)  # folderUPTODATE
		for dirpath, dirnames, filenames in walk(directory):  # walk() return a generator
			# dirpath = directory, for the first time
			# dirpath = subdirs of directory
			dirname = h.path_without_root(dirpath)
			if 'UPTODATE' not in dirname and dirname != '':
				dirs_maked.append(dirname)
			for filename in filenames:
				saved.append(path.join(dirname, filename))

		self.saved = saved
		self.dirs_maked = dirs_maked
		results = dict()
		results['saved'] = saved
		results['dirs_maked'] = dirs_maked
		json_filename = 'analysisS_' + '_'.join(directory.split('/')) + '.json'
		json_file = path.join(self.destination, json_filename)
		self.logger.info('Store analysis: ' + json_file)
		with open(json_file, 'w', encoding='utf-8') as myfile:
			myfile.write(json.dumps(results, indent=2))


	def save_files(self, to_save, safe_path, path_delicate):
		"""Copy the files in `to_save` in the `safe_path`."""
		errors = list()
		for filename in to_save:
			dst = path.join(safe_path, filename)
			self.logger.debug('Copy: '+ dst)
			src = path.join(path_delicate, filename)
			if not path.exists(src):
				self.logger.error("Source file not found: ", src)
				errors.append(filename)
				continue
			if not path.exists(path.dirname(dst)):
				self.logger.error("Destnation folder does not exist:", dst)
				errors.append(filename)
				continue
			try:
				copy2(src, dst)
			except FileNotFoundError as error:
				self.logger.error(str(error))
				errors.append(filename)
		return errors

	def update_files(self, to_update, safe_path, path_delicate):
		"""Update the files in `to_update`."""
		errors = list()
		for file_path in to_update:
			src = path.join(path_delicate, file_path)
			dst = path.join(safe_path, file_path)
			self.logger.debug('Update: '+ file_path)
			try:
				with open(src, 'rb') as myfile:
					content = myfile.read()
			except FileNotFoundError:
				self.logger.error('FileNotFoundError open update_files: ' + src, ' ' + dst)
				errors.append(file_path)
			try:
				with open(dst, 'wb') as myfile:
					myfile.write(content)
			except PermissionError:
				self.logger.error('PermissionError write update_files: ' + src, ' ' + dst)
		return errors

	def remove_files(self, to_del, safe_path_last):
		"""Remove the files in `to_del`."""
		errors = list()
		for filename in to_del:
			target = path.join(safe_path_last, filename)
			self.logger.info('Remove: ' + target)
			try:
				remove(target)
			except FileNotFoundError:
				self.logger.error('FileNotFoundError remove remove_files :' + target)
				errors.append(target)
		return errors

#!/usr/bin/python3

import asyncio
from shutil import copytree, copy2, rmtree
import logging
from logging.handlers import RotatingFileHandler
from os import path, listdir, mkdir, walk, remove, stat, chdir
from yaml import load, dump
import json


from .helpers import *


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
		file_handler = RotatingFileHandler('activity.log', maxBytes=1000000, backupCount=10)
		file_handler.setLevel(logging.DEBUG)
		formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
		file_handler.setFormatter(formatter)
		self.logger.addHandler(file_handler)
		# Log in the console
		stream_handler = logging.StreamHandler()
		stream_handler.setLevel(logging.DEBUG)
		#self.logger.addHandler(stream_handler)

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

		self.stop = False

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
				'extention': [],
				'local_path': '',
				'external_path': '',
				'timedelta': 1,
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
			self.logger.info('Make directory: ' + self.cfg_dir)
			mkdir(self.cfg_dir)
		with open(self.cfg_file, 'w') as ymlfile:
			dump(self.config, ymlfile)

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
			print('ERROR: del delicate dir, ValueError, safer')
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
		self.logger.info('Start saving with filters')
		for path_delicate, safe_path in self.safe_dirs.items():
			if safe_path['activate']:
				safe_path_filter = safe_path['FILTER']
				self.logger.info(path_delicate)
				self.logger.info('Make directory: ' + safe_path_filter)
				mkdir(safe_path_filter)  # e.g. safe_docs/my_work/my_workV--n

				if loop is None:
					loop = asyncio.get_event_loop()
				loop.run_until_complete(self.get_to_save(path_delicate))

				dirs_to_make = self.dirs_to_make
				to_save = self.list_files

				for dirname in dirs_to_make:
					#dirname = path_without_root(dirname)
					dirpath = path.join(safe_path_filter, dirname)
					self.logger.info('Make directory: ' + dirpath)
					if not path.exists(dirpath):
						mkdir(dirpath)  # e.g. safe_docs/my_work/my_workV--n/folder
				self.save_files(to_save, safe_path_filter, path_delicate)

		self.logger.info('Done')
		self.safe_dirs = self.get_dst_path()

	def copy_files(self):
		self.logger.info('Start copying')
		for path_delicate, safe_path in self.safe_dirs.items():
			if safe_path['activate']:
				self.logger.info('Saving ' + path_delicate)
				copytree(path_delicate, safe_path['COPY'])

		self.logger.info('Done')
		self.safe_dirs = self.get_dst_path()

	def update(self, loop=None):
		"""Update the safe directory.

		It create the directories requires and consider filtration rules.
		Copy the new files, remove the old ones.
		Remove directories trees is necessary.

		"""
		self.logger.info('Start updating')
		for path_delicate, safe_path in self.safe_dirs.items():
			if safe_path['activate']:
				self.logger.info(path_delicate)
				safe_path_last = safe_path['LAST']
				if not path.exists(safe_path_last):
					self.logger.info('Make directory: ' + safe_path_last)
					mkdir(safe_path_last)  # e.g. safe_docs/my_work/my_workUPTODATE

				if loop is None:
					loop = asyncio.get_event_loop()
				loop.run_until_complete(asyncio.wait([self.get_to_save(path_delicate), self.get_saved(safe_path_last),], loop=loop))

				dirs_to_save, dirs_maked = self.dirs_to_make, self.dirs_maked
				to_save, saved = self.list_files, self.saved

				# Make new folders
				# dirs_to_make: new directories, not yet copying
				dirs_to_make = missing_item(dirs_to_save, dirs_maked)
				for dirname in dirs_to_make:
					self.logger.info('Make directory: ' + path.join(safe_path_last, dirname))
					mkdir(path.join(safe_path_last, dirname))

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
		self.safe_dirs = self.get_dst_path()  # !!! probleme avec activate

	def compare(self, local_path, external_path, loop):
		"""
		Il faudrait une fenetre avec 3 onglets :
			- fichiers a copier : qui manquent dans la destination
			- fichiers a supprimer : qui ne sont plus dans la source
			- fichier a mettre a jour : qui sont déjà dans la destination et qui sont nouveau
				(ici attention il faut garder les fichiers les plus recents)
		... et on pourrait choisir quel fichier copier/supprimer/mettre a jour.
		Une option Garder les fichiers de la destination qui ne sont plus dans la sources.
		Une option Garder le dernier fichier (pour les fichiers presents dans la source et la destination).

		"""
		self.logger.info('Start comparing')

		loop.run_until_complete(self.get_to_save(local_path))

		local_dirs = self.dirs_to_make
		locals_files = self.list_files

		loop.run_until_complete(self.get_to_save(external_path))

		external_dirs = self.dirs_to_make
		external_files = self.list_files

		self.logger.info('Done')

		results = self.do_compare(local_dirs, locals_files, external_dirs, external_files)
		json_filename = 'compare'
		# linux system:
		json_filename += '_'.join(local_path.split('/'))
		json_filename += '_VS_' + '_'.join(external_path.split('/'))
		json_filename += '.json'
		json_file = path.join(self.destination, json_filename)
		self.logger.info('Store analysis compare: ' + json_file)
		with open(json_file, 'w') as myfile:
			myfile.write(json.dumps(results, indent=2))
		return results

	def do_compare(self, local_dirs, locals_files, external_dirs, external_files):
		dirs_to_make = missing_item(local_dirs, external_dirs)

		# Get new files, those not in external
		to_copy = missing_item(locals_files, external_files)

		# Get existing files in safe path
		to_update = combine_list(locals_files, external_files)

		# Get old files, thos not in local
		to_del = missing_item(external_files, locals_files)

		# Get old folders, to be deleted
		# dirs_to_del: directories copied, deleted in delicate drectory -> to delete from safe directory
		dirs_to_del = missing_item(external_dirs, local_dirs)

		results = dict()
		results['dirs_to_make'] = dirs_to_make
		results['dirs_to_del'] = dirs_to_del
		results['to_copy'] = to_copy  # files
		results['to_update'] = to_update  # files
		results['to_del'] = to_del  #files
		return results

	def compare_form_files(self, file_safe, file_weak, loop=None):
		with open(file_safe, 'r') as myfile:
			results_safe = json.loads(myfile.read())

		with open(file_weak, 'r') as myfile:
			results_weak = json.loads(myfile.read())

		local_dirs = results_safe['dirs_to_make']
		locals_files = results_safe['list_files']
		external_dirs = results_weak['dirs_to_make']
		external_files = results_weak['list_files']
		results = self.do_compare(local_dirs, locals_files, external_dirs, external_files)
		json_filename = 'compareF' + '_'.join(file_safe.split('/'))
		json_filename += '_VS_' + '_'.join(file_weak.split('/')) + '.json'
		json_file = path.join(self.destination, json_filename)
		self.logger.info('Store analysis compare from file: ' + json_file)
		with open(json_file, 'w') as myfile:
			myfile.write(json.dumps(results, indent=2))
		return results

	def execute(self, orders, local_path, external_path):
		for dirname in orders['dirs_to_make']:
			dirpath = path.join(external_path, dirname)
			self.logger.info('Make directory: ' + dirpath)
			mkdir(dirpath)
		self.save_files(orders['to_copy'], external_path, local_path)
		self.update_files(orders['to_update'], external_path, local_path)
		self.remove_files(orders['to_del'], external_path)
		for dirname in orders['dirs_to_del']:
			dirpath = path.join(external_path, dirname)
			self.logger.info('Remove tree: ' + dirpath)
			if path.exists(dirpath):
				rmtree(dirpath)

		self.logger.info('Done')

	async def get_to_save(self, directory):
		"""Return a list of file to save from a the given delicate directory, using `os.walk`.

		It make this list depending on exclusion rules.

		"""
		list_files = list()  # List of relatif path to each file
		dirs_to_make = list()  # List of directory to make in the safe root directory
		chdir(path.dirname(directory))
		directory_walk = path.basename(directory)
		for dirpath, dirnames, filenames in walk(directory_walk):  # walk() return a generator
			# dirpath = directory, for the first time
			# dirpath = subdirs of directory
			if self.stop:
				break
			self.logger.info(dirpath)

			# Exclude a directory name
			can = True
			for dirname in split_path(dirpath):
				if dirname in self.config['dirname']:
					can = False
			if not can:
				self.logger.info('Skip dirname: ' + dirpath)
				continue

			# Exclude a path
			can = True
			for dirname in self.config['dirpath']:
				if dirpath.find(dirname) != -1:
					can = False

			if can:
				dirname = path_without_root(dirpath)
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
		json_filename = 'analysisW' + '_'.join(directory.split('/')) + '.json'
		json_file = path.join(self.destination, json_filename)
		self.logger.info('Store analysis: ' + json_file)
		with open(json_file, 'w') as myfile:
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
			dirname = path_without_root(dirpath)
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
		with open(json_file, 'w') as myfile:
			myfile.write(json.dumps(results, indent=2))


	def save_files(self, to_save, safe_path, path_delicate):
		"""Copy the files in `to_save` in the `safe_path`."""
		for filename in to_save:
			dst = path.join(safe_path, filename)
			self.logger.info('Copy: '+ dst)
			try:
				copy2(path.join(path_delicate, filename), dst)
			except FileNotFoundError:
				print('FileNotFoundError copy save files: ' + filename)
				#TODO: put these file in a list and show it after, to notify what failed

	def update_files(self, to_update, safe_path, path_delicate):
		"""Update the files in `to_update`."""
		for file_path in to_update:
			src = path.join(path_delicate, file_path)
			dst = path.join(safe_path, file_path)
			try:
				if self.compare_file(src, dst):
					self.logger.info('Update: '+ file_path)
					with open(src, 'rb') as myfile:
						content = myfile.read()
					with open(dst, 'wb') as myfile:
						myfile.write(content)
			except FileNotFoundError:
				print('FileNotFoundError open update_files: ' + src, ' ' + dst)
				#TODO: put these file in a list and show it after, to notify what failed

	def remove_files(self, to_del, safe_path_last):
		"""Remove the files in `to_del`."""
		for filename in to_del:
			target = path.join(safe_path_last, filename)
			self.logger.info('Remove: ' + target)
			try:
				remove(target)
			except FileNotFoundError:
				print('FileNotFoundError remove remove_files :' + target)
				#TODO: put these file in a list and show it after, to notify what failed

	def compare_file(self, file1, file2):
		"""Return True if `file1` is most recent than `file2`."""
		stat_file1 = stat(file1)
		stat_file2 = stat(file2)
		return stat_file1.st_mtime > stat_file2.st_mtime

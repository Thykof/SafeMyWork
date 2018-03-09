#!/usr/bin/python3

from os import path, mkdir, stat, chdir, walk
from shutil import copy2

from safer import helpers

def mk_path(pathdir):  # TODO: unit test
	"""Make the path and the folder to `pathdir`"""
	basename_dir = path.dirname(pathdir)
	if not path.exists(basename_dir):
		mk_path(basename_dir)
	else:
		mkdir(pathdir)

def save_files(files, dst, src):  #TODO: unit test
	errors = list()
	for filename in files:
		src_path = path.join(src, filename)
		dst_path = path.join(dst, filename)
		if not path.exists(path.dirname(dst_path)):
			mk_path(path.dirname(dst_path))
		if path.exists(path.dirname(dst_path)) and path.exists(src_path):
			copy2(src_path, dst_path)
		else:
			errors.append(filename)
	return errors

class Sync(object):
	def __init__(self, local_path, ext_path):
		super(Sync, self).__init__()
		# Varaibles to set:
		self.local_path = local_path
		self.ext_path = ext_path

		self.stop = False

		self.config = dict()
		self.config['dirname'] = list()
		self.config['dirpath'] = list()
		self.config['filename'] = list()
		self.config['extention'] = list()

		# Default value for these variables:
		self.safe_doc = path.join(path.expanduser('~'), 'safe_docs')

		self.ext_files = None
		self.locals_files = None
		self.comparison = None

	def set_safe_doc(self, safe_doc):
		self.safe_doc = safe_doc

	def set_config(self, config):
		self.config = config

	def scan_dir(self, dirname):
		list_files = list()  # List of relatif path to each file
		chdir(path.dirname(dirname))
		walked_dir = path.basename(dirname)
		for info in walk(walked_dir):  # walk() return a generator
			dirpath, filenames = info[0], info[2]
			# dirpath: dirname, for the first time
			# dirpath: subdirs of dirname
			if self.stop:
				break

			# Exclude a dirname name
			can = True
			for dirname in helpers.split_path(dirpath):
				if dirname in self.config['dirname']:
					can = False

			# Exclude a path
			can = True
			for dirname in self.config['dirpath']:
				if dirpath.find(dirname) != -1:
					can = False
			if can:
				dirname = helpers.path_without_root(dirpath)
				# Take all files
				for filename in filenames:
					# Find the extension
					ext = path.splitext(filename)[1][1:]
					if filename not in self.config['filename'] and ext not in self.config['extention']:
						list_files.append(path.join(dirname, filename))
					if self.stop:
						break

		json_filename = 'analysisW' + '_'.join(dirname.split('/')) + '.json'
		helpers.store(list_files, self.safe_doc, json_filename)
		return list_files

	def scan_compare(self, local_path=None, ext_path=None):
		# Fill self.locals_files and self.ext_files
		if local_path is None:
			local_path = self.local_path
		if ext_path is None:
			ext_path = self.ext_path

		self.locals_files = self.scan_dir(local_path)
		self.ext_files = self.scan_dir(ext_path)
		self.compare()

	def sync(self, comparison=None):
		if comparison is None:
			comparison = self.comparison
		helpers.store(comparison, self.safe_doc, 'analysisSYNC')
		errors1 = save_files(comparison['local'], comparison['paths'][0], comparison['paths'][1])
		errors2 = save_files(comparison['ext'], comparison['paths'][1], comparison['paths'][0])
		self.errors = (errors1, errors2)

	def exec_sync(self, local_path=None, ext_path=None):
		# scan_dir, compare, solve, sync
		if local_path is None:
			local_path = self.local_path
		if ext_path is None:
			ext_path = self.ext_path

		self.scan_compare(local_path, ext_path)
		self.compare_results = self.compare()
		self.solve_conflicts()
		return self.sync()

	def compare(self, locals_files=None, ext_files=None):
		# Fill self.comparison
		# locals_files and ext_files are given by self.scan_dir
		if locals_files is None:
			locals_files = self.locals_files
		if ext_files is None:
			ext_files = self.ext_files

		comparison = dict()
		conflicts = list()
		comparison['local'] = helpers.missing_item(ext_files, locals_files)
		comparison['ext'] = helpers.missing_item(locals_files, ext_files)
		for filename in helpers.combine_list(locals_files, ext_files):
			# stat:
			stat_local = stat(path.join(self.local_path, filename))
			stat_ext = stat(path.join(self.ext_path, filename))
			# size:
			size_local = stat_local.st_size
			size_ext = stat_ext.st_size
			# date (the older has st_mtime lower):
			date_local = stat_local.st_mtime
			date_ext = stat_ext.st_mtime
			ss = False
			sd = False
			if date_ext == date_local:
				sd = True
			if size_ext == size_local:
				ss = True
			if ss and sd:
				pass
			else:
				conflicts.append([filename, (size_local, size_ext), (date_local, date_ext)])
		comparison['conflicts'] = conflicts
		comparison['paths'] = self.local_path, self.ext_path  # needed by ConflictDialog
		helpers.store(comparison, self.safe_doc, 'analysisSYNCAVANT')

		self.comparison = comparison

	def solve_conflicts(self):
		conflicts = self.comparison['conflicts']
		for num, fileinfo in enumerate(conflicts):
			if fileinfo[2][0] > fileinfo[2][1]:  # local is more recent
				self.change_dst('local', num)
			else:
				self.change_dst('ext', num)

	def change_dst(self, path_type, num):
		conflicts = self.comparison['conflicts']
		if path_type == 'ext':
			if conflicts[num][0] not in self.comparison['local']:
				self.add_in_local(conflicts[num][0])
			if conflicts[num][0] in self.comparison['ext']:
				self.remove_in_ext(conflicts[num][0])
		else:  # path_type == 'local'
			if conflicts[num][0] not in self.comparison['ext']:
				self.add_in_ext(conflicts[num][0])
			if conflicts[num][0] in self.comparison['local']:
				self.remove_in_local(conflicts[num][0])

	def add_in_local(self, filename):
		self.comparison['local'].append(filename)

	def remove_in_local(self, filename):
		self.comparison['local'].remove(filename)

	def add_in_ext(self, filename):
		self.comparison['ext'].append(filename)

	def remove_in_ext(self, filename):
		self.comparison['ext'].remove(filename)

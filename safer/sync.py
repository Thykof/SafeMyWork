#!/usr/bin/python3

from os import path, mkdir, stat
from shutil import copy2

from safer.helpers import missing_item, combine_list, store


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

		# Default value for these variables:
		self.safe_doc = path.join(path.expanduser('~'), 'safe_docs')

	def set_safe_doc(self, safe_doc):
		self.safe_doc = safe_doc

	def run(self, locals_files, ext_files):  # need to solve conflicts!
		return self.sync(self.compare(locals_files, ext_files))

	def compare(self, locals_files, ext_files):
		# locals_files and ext_files are given by Scan
		orders = dict()
		conflicts = list()
		orders['local'] = missing_item(ext_files, locals_files)
		orders['ext'] = missing_item(locals_files, ext_files)
		for filename in combine_list(locals_files, ext_files):
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
		orders['conflicts'] = conflicts
		orders['paths'] = self.local_path, self.ext_path  # needed by ConflictDialog
		store(orders, self.safe_doc, 'analysisSYNCAVANT')
		return orders

	def sync(self, orders):
		store(orders, self.safe_doc, 'analysisSYNC')
		errors1 = save_files(orders['local'], orders['paths'][0], orders['paths'][1])
		errors2 = save_files(orders['ext'], orders['paths'][1], orders['paths'][0])
		return errors1, errors2

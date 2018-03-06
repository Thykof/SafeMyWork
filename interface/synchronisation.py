#!/usr/bin/python3

import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib, Gio

from .helpers import open_folder as show_dir
from .dialogs.dialog import folder_chooser
from .dialogs.conflict import ConflictDialog
from .dialogs.dialog import ConfirmDialog, AbortDialog
from safer import sync

class SyncThread(threading.Thread):
	def __init__(self, target, callback):
		super().__init__()
		self.daemon = True
		self.target = target
		self.callback = callback

	def run(self):
		print('run')
		self.target()
		print('apres target')
		GLib.idle_add(self.callback)
		print('end run')

class SynchronisationGrid(Gtk.Grid):
	def __init__(self, parent, safer):
		Gtk.Grid.__init__(self)
		self.thread = SyncThread(None, None)
		self.state = ''

		# Varaibles
		self.parent = parent
		self.safer = safer

		# Properties
		self.set_column_spacing(5)
		self.set_row_spacing(5)

		# Widgets
		button_show_local = Gtk.Button.new_with_label('Open local folder')
		button_show_local.connect('clicked', self.open_folder, True)
		self.attach(button_show_local, 0, 0, 1, 1)

		button_choose_local = Gtk.Button.new_with_label("Select local folder")
		button_choose_local.connect('clicked', self.select_local)
		self.attach(button_choose_local, 1, 0, 1, 1)

		if self.safer.config['local_path'] == '':
			self.label_local = Gtk.Label("< select local folder >")
		else:
			self.label_local = Gtk.Label(self.safer.config['local_path'])
		self.attach(self.label_local, 0, 1, 2, 1)

		button_show_external = Gtk.Button.new_with_label('Open external folder')
		button_show_external.connect('clicked', self.open_folder, False)
		self.attach(button_show_external, 0, 2, 1, 1)
		button_choose_external = Gtk.Button.new_with_label("Select external folder")
		button_choose_external.connect('clicked', self.select_ext)
		self.attach(button_choose_external, 1, 2, 1, 1)

		if self.safer.config['external_path'] == '':
			self.label_external = Gtk.Label("< Select external folder >")
		else:
			self.label_external = Gtk.Label(self.safer.config['external_path'])
		self.attach(self.label_external, 0, 3, 2, 1)

		box_sync = Gtk.Box()
		self.spinner = Gtk.Spinner()
		self.button_compare = Gtk.Button.new_with_label('Sync / Compare')
		self.button_compare.connect('clicked', self.compare)
		box_sync.pack_start(self.button_compare, True, True, 5)
		box_sync.pack_start(self.spinner, False, False, 5)
		self.attach(box_sync, 0, 4, 2, 1)

	def select_local(self, button):
		folder = folder_chooser(self.parent)
		if folder:
			self.label_local.set_text(folder)
			self.safer.config['local_path'] = folder

	def select_ext(self, button):
		folder = folder_chooser(self.parent)
		if folder:
			self.label_external.set_text(folder)
			self.safer.config['external_path'] = folder

	def compare(self, button):
		local_dir = self.label_local.get_text()
		ext_dir = self.label_external.get_text()
		if local_dir != '' and ext_dir != '' and local_dir[0] != '<' and ext_dir[0] != '<':
			if not self.thread.is_alive():
				self.spinner.start()
				self.parent.info_label.set_text("Sync runing")
				#self.dialog = AbortDialog(self.parent)
				#self.dialog.run()
				self.do_compare(local_dir, ext_dir)
			else:
				self.parent.info_label.set_text("Already runing")
		else:
			self.parent.info_label.set_text("Please select folders")

	def do_compare(self, local_dir, ext_dir):
		self.mysync = sync.Sync(local_dir, ext_dir)
		self.thread = SyncThread(self.mysync.scan_compare, self.after_scan_compare)
		self.thread.start()

	def after_scan_compare(self):
		print('after_scan_compare')
		#self.dialog.destroy()  # AbortDialog
		self.show_compare_results()

	def show_compare_results(self):
		compare_results = self.mysync.comparison
		cancel = False
		max_conflicts = 2
		if len(compare_results['conflicts']) > 0:
			conflict_dialog = ConflictDialog(self.parent, self.mysync, max_conflicts)
			response = conflict_dialog.run()
			if response == Gtk.ResponseType.OK:
				compare_results = conflict_dialog.comparison
			else:
				cancel = True
			if len(compare_results['conflicts']) > max_conflicts and self.safer.config['advanced'] == False:
				if conflict_dialog.switch.get_active():
					self.mysync.solve_conflicts()
			conflict_dialog.destroy()

		if not cancel:
			confirm_dialog = ConfirmDialog(self.parent, compare_results)
			response = confirm_dialog.run()
			if response == Gtk.ResponseType.OK:
				# Work:
				self.thread.join()
				self.thread = SyncThread(self.mysync.sync, self.after_sync)
				self.thread.start()
				self.state = "Done"
			else:
				self.state = "Sync aborted"
				self.after_sync()
			confirm_dialog.destroy()
		else:
			self.state = "Sync aborted"
			self.after_sync()

	def after_sync(self):
		print('after_sync')
		self.spinner.stop()
		self.parent.info_label.set_text(self.state)

	def open_folder(self, button, local):
		if local:
			if self.label_local.get_text()[0] != '<':
				show_dir(self.label_local.get_text())
			else:
				self.parent.info_label.set_text("Please select local folder")
		else:
			if self.label_external.get_text()[0] != '<':
				show_dir(self.label_external.get_text())
			else:
				self.parent.info_label.set_text("Please select external folder")

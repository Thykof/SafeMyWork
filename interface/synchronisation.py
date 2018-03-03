#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib

from .helpers import open_folder as show_dir
from .dialog import folder_chooser
from .conflict import ConflictDialog, ConfirmDialog
from safer import scan, sync

class SynchronisationGrid(Gtk.Grid):
	def __init__(self, parent, safer):
		Gtk.Grid.__init__(self)

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
		if self.label_local.get_text() != "" and self.label_external.get_text() != '':
			GLib.idle_add(self.do_compare)
			self.parent.info_label.set_text("Sync runing")
		else:
			self.parent.info_label.set_text("Please select folders")
			self.select_all.set_active(False)

	def do_compare(self, path1=None, path2=None):
		self.spinner.start()

		def compare():
			myscan = scan.Scan()
			files1 = myscan.scan_dir(self.label_local.get_text())
			files2 = myscan.scan_dir(self.label_external.get_text())
			self.mysync = sync.Sync(self.label_local.get_text(), self.label_external.get_text())
			return self.mysync.compare(files1, files2)

		compare_results = compare()
		self.show_compare_results(compare_results)
		self.spinner.stop()

	def show_compare_results(self, compare_results):
		cancel = False
		if len(compare_results['conflicts']) > 0:
			conflict_dialog = ConflictDialog(self.parent, compare_results)
			response = conflict_dialog.run()
			if response == Gtk.ResponseType.OK:
				compare_results = conflict_dialog.comparison
			else:
				cancel = True
			conflict_dialog.destroy()

		if not cancel:
			confirm_dialog = ConfirmDialog(self.parent, compare_results)
			response = confirm_dialog.run()
			if response == Gtk.ResponseType.OK:
				GLib.idle_add(self.mysync.sync, compare_results)
				self.parent.info_label.set_text("Done")
			else:
				self.parent.info_label.set_text("Sync aborted")
			confirm_dialog.destroy()

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

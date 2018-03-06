#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from os import path

class DelDirDialog(Gtk.Dialog):

	def __init__(self, parent, list_delicate):
		Gtk.Dialog.__init__(self, "", parent, 0,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 Gtk.STOCK_OK, Gtk.ResponseType.OK))
		self.set_modal(True)
		self.set_resizable(False)
		self.set_border_width(10)
		# Result values:
		self.dirname = None
		self.diriter = None

		box = self.get_content_area()
		box.set_spacing(6)
		combo = Gtk.ComboBox.new_with_model(list_delicate)
		combo.set_hexpand(True)
		combo.connect("changed", self.on_combo_changed)
		renderer_text = Gtk.CellRendererText()
		combo.pack_start(renderer_text, True)
		combo.add_attribute(renderer_text, "text", 0)
		box.pack_start(combo, False, False, True)

		#box.add()
		self.show_all()

	def on_combo_changed(self, combo):
		self.diriter = combo.get_active_iter()
		if self.diriter is not None:  # otherwise raise error when destroy dialog
			self.dirname = combo.get_model().get_value(self.diriter, 0)

class ConfirmDialog(Gtk.Dialog):
	def __init__(self, parent, orders):
		Gtk.Dialog.__init__(self, "Confirm", parent, 0,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			Gtk.STOCK_OK, Gtk.ResponseType.OK))

		# Varaibles
		self.parent = parent
		self.orders = orders

		# Properties
		self.set_border_width(10)
		self.set_modal(True)
		self.set_default_size(800, 250)

		# Content
		self.box = self.get_content_area()
		self.initialise_box()

		self.show_all()

	def initialise_box(self):
		self.box.set_spacing(6)
		box_wrapper = Gtk.Box()

		files_lost = list()
		conflict_files = list()
		files_create = list()
		for fileinfo in self.orders['conflicts']:
			conflict_files.append(fileinfo[0])
		for filename in self.orders['local']:
			path_file = path.join(self.orders['paths'][0], filename)
			if filename in conflict_files:
				files_lost.append(path_file)
			else:
				files_create.append(path_file)

		for filename in self.orders['ext']:
			path_file = path.join(self.orders['paths'][0], filename)
			if filename in conflict_files:
				files_lost.append(path_file)
			else:
				files_create.append(path_file)

		box_lost = Gtk.VBox()
		box_lost.pack_start(Gtk.Label('These files will be lost:'), False, False, 5)
		box_filenames = Gtk.VBox()
		scrolled = Gtk.ScrolledWindow()
		for filename in files_lost[:1000]:
			box_filenames.pack_start(Gtk.Label(filename), False, False, 1)

		scrolled.add(box_filenames)
		box_lost.pack_start(scrolled, True, True, 2)

		box_create = Gtk.VBox()
		box_create.pack_start(Gtk.Label('These files will be create:'), False, False, 5)
		box_filenames = Gtk.VBox()
		scrolled = Gtk.ScrolledWindow()
		for filename in files_create:
			box_filenames.pack_start(Gtk.Label(filename), False, False, 1)
		scrolled.add(box_filenames)
		box_create.pack_start(scrolled, True, True, 2)

		box_wrapper.pack_start(box_lost, True, True, 5)
		box_wrapper.pack_start(box_create, True, True, 5)

		self.box.pack_start(box_wrapper, True, True, 0)

class AbortDialog(Gtk.Dialog):
	def __init__(self, parent):
		Gtk.Dialog.__init__(self, "Work in progress...", parent, 0,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
		self.parent = parent

		self.set_modal(True)

		label = Gtk.Label("Work in progress...")

		box = self.get_content_area()
		box.add(label)
		self.show_all()

	def close(self):
		self.destroy()

class ErrorsDialog(Gtk.Dialog):
	def __init__(self, parent, errors):
		Gtk.Dialog.__init__(self, "Files not found", parent, 0,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
		self.parent = parent
		self.set_modal(True)

		msg = 'These files were not found:'
		for filename in errors:
			msg += filename + '\n'
		label = Gtk.Label(msg)

		box = Gtk.VBox()
		box.pack_start(Gtk.Label('These files were not found:'), True, False, 3)
		box.pack_start(label, True, False, 3)

		scrolled = Gtk.ScrolledWindow()
		scrolled.set_min_content_height(300)
		scrolled.add(box)
		box = self.get_content_area()
		box.add(scrolled)
		self.show_all()

def folder_chooser(parent, is_folder=True, folder=None, msg=None):
	if not is_folder:
		if msg is None:
			msg = "Select a folder"
		dialog = Gtk.FileChooserDialog(msg, parent,
			Gtk.FileChooserAction.OPEN,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		if folder:
			dialog.set_current_folder(folder)
	else:
		if msg is None:
			msg = "Select a file"
		dialog = Gtk.FileChooserDialog(msg, parent,
			Gtk.FileChooserAction.SELECT_FOLDER,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 "Select", Gtk.ResponseType.OK))
	dialog.set_default_size(800, 400)

	response = dialog.run()
	if response == Gtk.ResponseType.OK:
		result = dialog.get_filename()
	else:
		result = None
	dialog.destroy()
	return result

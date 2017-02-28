# -*- coding: utf-8 -*-
#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from os import path

def del_dir_dialog(parent, directory):
	dialog = Gtk.MessageDialog(parent, 0, Gtk.MessageType.QUESTION,
			Gtk.ButtonsType.YES_NO, "Ne plus surveiller " + directory + " ?")
	response = dialog.run()
	return response == Gtk.ResponseType.YES, dialog

class Settings_dial(Gtk.Dialog):
	"""docstring for Settings"""
	def __init__(self, parent):
		Gtk.Dialog.__init__(self, 'Préférences', parent, 0)
		self.parent = parent
		self.set_modal(True)
		self.set_resizable(False)
		self.set_border_width(10)
		self.connect('delete-event', self.close)
		box = self.get_content_area()
		box.set_spacing(6)

		box_time = self.create_box_time()
		box_ext = self.create_box_ext()
		box_files = self.create_box_files()
		box_dirs = self.create_box_dirs()
		box_archive_dir = self.create_box_archive_dir()
		button_close = Gtk.Button.new_with_label('Femrer')
		button_close.connect('clicked', self.close)

		# Pack boxes
		box.pack_start(box_time, False, False, 0)
		box.pack_start(box_ext, False, False, 0)
		box.pack_start(box_files, False, False, 0)
		box.pack_start(box_dirs, False, False, 0)
		box.pack_start(box_archive_dir, False, False, 0)
		box.pack_start(button_close, False, False, 0)
		self.show_all()

	def create_box_time(self):
		# Set timedelta:
		box_time = Gtk.Box(spacing=6)
		adjustment = Gtk.Adjustment(10, 1, 60, 10, 10, 0)
		self.spinbutton = Gtk.SpinButton(adjustment=adjustment)
		self.spinbutton.set_digits(0)
		self.spinbutton.set_value(self.parent.time_delta)
		timedelta_button = Gtk.Button.new_with_label('Changer')
		timedelta_button.connect('clicked', self.change_timedelta)
		box_time.pack_start(Gtk.Label('Scan tous les :'), False, False, 0)
		box_time.pack_start(self.spinbutton, False, False, 0)
		box_time.pack_start(Gtk.Label('Minutes. '), False, False, 0)
		box_time.pack_start(timedelta_button, False, False, 0)
		return box_time

	def create_box_ext(self):
		# Exclude extenstions:
		box_ext = Gtk.Box(spacing=6)
		box_ext.pack_start(Gtk.Label('Extensions : '), False, False, 0)
		ext_list = Gtk.ComboBoxText.new_with_entry()
		button_add_ext = Gtk.Button.new_with_label('Ajouter')
		button_add_ext.connect('clicked', lambda arg: self.add('extention', ext_list))
		button_del_ext = Gtk.Button.new_with_label('Supprimer')
		button_del_ext.connect('clicked', lambda arg: self.delete('extention', ext_list))
		box_ext.pack_start(ext_list, False, False, 0)
		box_ext.pack_start(button_add_ext, False, False, 0)
		box_ext.pack_start(button_del_ext, False, False, 0)
		for ext in self.parent.safer.config['extention']:
			ext_list.append_text(ext)
		return box_ext

	def create_box_files(self):
		# Exclude files:
		box_files = Gtk.Box(spacing=6)
		box_files.pack_start(Gtk.Label('Fichiers : '), False, False, 0)
		file_list = Gtk.ComboBoxText.new_with_entry()
		button_add_file = Gtk.Button.new_with_label('Ajouter')
		button_add_file.connect('clicked', lambda arg: self.add('filename', file_list))
		button_del_file = Gtk.Button.new_with_label('Supprimer')
		button_del_file.connect('clicked', lambda arg: self.delete('filename', file_list))
		box_files.pack_start(file_list, False, False, 0)
		box_files.pack_start(button_add_file, False, False, 0)
		box_files.pack_start(button_del_file, False, False, 0)
		for file in self.parent.safer.config['filename']:
			file_list.append_text(file)
		return box_files

	def create_box_dirs(self):
		# Exclude directories:
		box_dirs = Gtk.Box(spacing=6)
		box_dirs.pack_start(Gtk.Label('Dossiers : '), False, False, 0)
		dirs_list = Gtk.ComboBoxText.new_with_entry()
		button_add_dirs = Gtk.Button.new_with_label('Ajouter')
		button_add_dirs.connect('clicked', lambda arg: self.add('dirname', dirs_list))
		button_del_dirs = Gtk.Button.new_with_label('Supprimer')
		button_del_dirs.connect('clicked', lambda arg: self.delete('dirname', dirs_list))
		box_dirs.pack_start(dirs_list, False, False, 0)
		box_dirs.pack_start(button_add_dirs, False, False, 0)
		box_dirs.pack_start(button_del_dirs, False, False, 0)
		for dirs in self.parent.safer.config['dirname']:
			dirs_list.append_text(dirs)
		return box_dirs

	def create_box_archive_dir(self):
		# Archive directory:
		box_archive_dir = Gtk.Box(spacing=6)
		box_archive_dir.pack_start(Gtk.Label('Dossier archive : '), False, False, 0)
		self.archive_entry = Gtk.Entry()
		self.archive_entry.set_text(self.parent.safer.destination)
		archive_button = Gtk.Button.new_with_label('Changer')
		archive_button.connect('clicked', self.change_archive_dir)
		box_archive_dir.pack_start(self.archive_entry, False, False, 0)
		box_archive_dir.pack_start(archive_button, False, False, 0)
		return box_archive_dir


	def close(self, *args):
		self.destroy()

	def add(self, elt, combo_list):
		tree_iter = combo_list.get_active_iter()
		if tree_iter is None:
			new = combo_list.get_child().get_text()
			if new not in self.parent.safer.config[elt]:
				combo_list.append_text(new)
				self.parent.safer.config[elt].append(new)

	def delete(self, elt, combo_list):
		tree_iter = combo_list.get_active_iter()
		if tree_iter is not None:
			model = combo_list.get_model()
			new = model[tree_iter][0]
			combo_list.remove(int(combo_list.get_active()))
			self.parent.safer.config[elt].remove(new)

	def change_timedelta(self, button):
		timedelta = int(self.spinbutton.get_value())
		self.parent.time_delta = timedelta

	def change_archive_dir(self, button):
		new = self.archive_entry.get_text()
		if new != '':
			self.parent.safer.set_destination(new)

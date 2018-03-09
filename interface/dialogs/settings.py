#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class SettingsDialog(Gtk.Dialog):
	"""Setting dialog

	Can change:
		- the time between two scan
		- the extentions to avoid
		- the filenames to avoid
		- the directories to avoid
		- the paths to avoid

	"""
	def __init__(self, parent):
		Gtk.Dialog.__init__(self, 'Préférences', parent, 0)
		self.parent = parent
		self.set_modal(True)
		self.set_resizable(False)
		self.set_border_width(10)
		self.connect('delete-event', self.close)
		box = self.get_content_area()
		box.set_spacing(6)

		button_close = Gtk.Button.new_with_label('Close')
		button_close.connect('clicked', self.close)

		# Set timedelta:
		box_time = Gtk.Box(spacing=6)
		adjustment = Gtk.Adjustment(10, 1, 60, 10, 10, 0)
		self.spinbutton = Gtk.SpinButton(adjustment=adjustment)
		self.spinbutton.set_digits(0)
		self.spinbutton.set_value(self.parent.safer.config['timedelta'])
		box_time.pack_start(Gtk.Label('Scan every :'), False, False, 0)
		box_time.pack_start(self.spinbutton, False, False, 0)
		box_time.pack_start(Gtk.Label('minutes. '), False, False, 0)

		# Exclude extenstions:
		box_ext = Gtk.Box(spacing=6)
		box_ext.pack_start(Gtk.Label('Extensions : '), False, False, 0)
		ext_list = Gtk.ComboBoxText.new_with_entry()
		button_add_ext = Gtk.Button.new_with_label('Add')
		button_add_ext.connect('clicked', lambda arg: self.add('extention', ext_list))
		button_del_ext = Gtk.Button.new_with_label('Del')
		button_del_ext.connect('clicked', lambda arg: self.delete('extention', ext_list))
		box_ext.pack_start(ext_list, False, False, 0)
		box_ext.pack_start(button_add_ext, False, False, 0)
		box_ext.pack_start(button_del_ext, False, False, 0)
		for ext in self.parent.safer.config['extention']:
			ext_list.append_text(ext)

		# Exclude files:
		box_files = Gtk.Box(spacing=6)
		box_files.pack_start(Gtk.Label('Files: '), False, False, 0)
		file_list = Gtk.ComboBoxText.new_with_entry()
		button_add_file = Gtk.Button.new_with_label('Add')
		button_add_file.connect('clicked', lambda arg: self.add('filename', file_list))
		button_del_file = Gtk.Button.new_with_label('Del')
		button_del_file.connect('clicked', lambda arg: self.delete('filename', file_list))
		box_files.pack_start(file_list, False, False, 0)
		box_files.pack_start(button_add_file, False, False, 0)
		box_files.pack_start(button_del_file, False, False, 0)
		for file in self.parent.safer.config['filename']:
			file_list.append_text(file)

		# Exclude directories:
		box_dirs = Gtk.Box(spacing=6)
		box_dirs.pack_start(Gtk.Label('Folders: '), False, False, 0)
		dirs_list = Gtk.ComboBoxText.new_with_entry()
		button_add_dirs = Gtk.Button.new_with_label('Add')
		button_add_dirs.connect('clicked', lambda arg: self.add('dirname', dirs_list))
		button_del_dirs = Gtk.Button.new_with_label('Del')
		button_del_dirs.connect('clicked', lambda arg: self.delete('dirname', dirs_list))
		box_dirs.pack_start(dirs_list, False, False, 0)
		box_dirs.pack_start(button_add_dirs, False, False, 0)
		box_dirs.pack_start(button_del_dirs, False, False, 0)
		for dirs in self.parent.safer.config['dirname']:
			dirs_list.append_text(dirs)

		# Exclude paths:
		box_paths = Gtk.Box(spacing=6)
		box_paths.pack_start(Gtk.Label('Paths: '), False, False, 0)
		paths_list = Gtk.ComboBoxText.new_with_entry()
		button_add_paths = Gtk.Button.new_with_label('Add')
		button_add_paths.connect('clicked', lambda arg: self.add('dirpath', paths_list))
		button_del_paths = Gtk.Button.new_with_label('Del')
		button_del_paths.connect('clicked', lambda arg: self.delete('dirpath', paths_list))
		box_paths.pack_start(paths_list, False, False, 0)
		box_paths.pack_start(button_add_paths, False, False, 0)
		box_paths.pack_start(button_del_paths, False, False, 0)
		for dirs in self.parent.safer.config['dirpath']:
			paths_list.append_text(dirs)

		# Archive directory:
		box_archive_dir = Gtk.Box(spacing=6)
		box_archive_dir.pack_start(Gtk.Label('Safe folder: '), False, False, 0)
		self.archive_label = Gtk.Label()
		self.archive_label.set_text(self.parent.safer.destination)
		self.archive_change_button = Gtk.Button.new_with_label('Change')
		self.archive_change_button.connect('clicked', self.change_archive)
		box_archive_dir.pack_start(self.archive_label, False, False, 0)
		box_archive_dir.pack_start(self.archive_change_button, False, False, 0)

		# Advanced:
		box_advanced = Gtk.VBox(spacing=10)
		box_advanced.pack_start(Gtk.Label('Advanced'), False, False, 0)
		box_disable = Gtk.Box()
		box_disable.pack_start(Gtk.Label('Disable safe restrictions:'), False, False, 0)
		switch_disable = Gtk.Switch()
		switch_disable.set_active(self.parent.safer.config['advanced'])
		switch_disable.connect('notify::active', self.on_switch_disable)
		box_disable.pack_start(switch_disable, False, False, 0)
		box_advanced.pack_start(box_disable, False, False, 0)

		# Pack boxes
		box.pack_start(box_time, False, False, 0)
		box.pack_start(Gtk.Label('Exclusion rules: '), False, False, 0)
		box.pack_start(box_ext, False, False, 0)
		box.pack_start(box_files, False, False, 0)
		box.pack_start(box_dirs, False, False, 0)
		box.pack_start(box_paths, False, False, 0)
		box.pack_start(box_archive_dir, False, False, 0)
		box.pack_start(box_advanced, False, False, 10)
		box.pack_start(button_close, False, False, 0)
		self.show_all()

	def close(self, *args):
		"""Save the changes and close."""
		# Set new timedelta
		timedelta = int(self.spinbutton.get_value())
		self.parent.safer.config['timedelta'] = timedelta

		# Set new safe path
		new = self.archive_label.get_text()
		if new != '':
			self.parent.safer.set_destination(new)
		self.destroy()

	def add(self, elt, combo_list):
		"""Add the `elt` in the `combo_list`."""
		tree_iter = combo_list.get_active_iter()
		if tree_iter is None:
			new = combo_list.get_child().get_text()
			if new not in self.parent.safer.config[elt]:
				combo_list.append_text(new)
				self.parent.safer.config[elt].append(new)

	def delete(self, elt, combo_list):
		"""Delete the `elt` in the `combo_list`."""
		tree_iter = combo_list.get_active_iter()
		if tree_iter is not None:
			model = combo_list.get_model()
			new = model[tree_iter][0]
			combo_list.remove(int(combo_list.get_active()))
			self.parent.safer.config[elt].remove(new)

	def change_archive(self, button):
		new_folder = folder_chooser(self)
		if new_folder:
			self.archive_label.set_text(new_folder)

	def on_switch_disable(self, switch, active):
		self.parent.safer.config['advanced'] = switch.get_active()

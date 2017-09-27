#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

import asyncio

from .helpers import open_folder

class SynchronisationGrid(Gtk.Grid):
	def __init__(self, safer):
		Gtk.Grid.__init__(self)

		# Varaibles
		self.safer = safer
		self.loop = asyncio.get_event_loop()

		# Properties
		self.set_column_spacing(5)
		self.set_row_spacing(5)

		# Widgets
		self.local_path = ""
		self.external_path = ""
		button_show_local = Gtk.Button.new_with_label('Dossier local')
		button_show_local.connect('clicked', open_folder, self.local_path)
		self.attach(button_show_local, 0, 0, 1, 1)
		button_show_external = Gtk.Button.new_with_label('Dossier externe')
		button_show_external.connect('clicked', open_folder, self.external_path)
		self.attach(button_show_external, 1, 0, 1, 1)
		# TODO: add little icon to symbolize file explorer

		label_select_folder = Gtk.Label("Selection du dossier local :")
		self.attach(label_select_folder, 0, 1, 2, 1)

		local_store = Gtk.ListStore(str)
		for path_delicate, safe_path in self.safer.safe_dirs.items():
			local_store.append([path_delicate])
		self.local_combo = Gtk.ComboBox.new_with_model(local_store)
		self.local_combo.connect("changed", self.on_local_combo_changed)
		renderer_text = Gtk.CellRendererText()
		self.local_combo.pack_start(renderer_text, True)
		self.local_combo.add_attribute(renderer_text, "text", 0)
		self.attach(self.local_combo, 0, 2, 2, 1)

		label_select_folder = Gtk.Label("Selection du dossier externe :")
		self.attach(label_select_folder, 0, 3, 2, 1)

		self.external_combo = Gtk.ComboBoxText.new_with_entry()
		self.external_combo.connect('changed', self.on_external_combo_changed)
		self.external_combo.append_text(self.safer.config['safe_dir'])
		self.attach(self.external_combo, 0, 4, 2, 1)

		self.button_compare = Gtk.Button.new_with_label('Comparer')
		self.button_compare.connect('clicked', self.compare)
		self.button_execute = Gtk.Button.new_with_label('Executer')
		self.button_execute.connect('clicked', self.execute_compare)
		self.button_execute.set_sensitive(False)
		self.attach(self.button_compare, 0, 5, 1, 1)
		self.attach(self.button_execute, 1, 5, 1, 1)

		# List files:
		label_select_files = Gtk.Label("Selections des fichiers :")
		self.attach(label_select_files, 0, 6, 2, 1)
		self.scrolled_win_select_file = Gtk.ScrolledWindow()
		self.scrolled_win_select_file.set_min_content_width(600)
		self.attach(self.scrolled_win_select_file, 0, 7, 2, 1)

		self.listfile = Gtk.ListStore(str, bool, str)
		self.treeview_file = Gtk.TreeView.new_with_model(self.listfile)

		renderer_text = Gtk.CellRendererText()
		column_text = Gtk.TreeViewColumn("Fichier", renderer_text, text=0)
		self.treeview_file.append_column(column_text)

		renderer_toggle = Gtk.CellRendererToggle()
		renderer_toggle.connect("toggled", self.on_cell_toggled_file)
		tree_view_column_toggle = Gtk.TreeViewColumn("Modifier", renderer_toggle, active=1)
		self.treeview_file.append_column(tree_view_column_toggle)

		renderer_pixbuf = Gtk.CellRendererPixbuf()
		column_pixbuf = Gtk.TreeViewColumn("Image", renderer_pixbuf, icon_name=2)
		self.treeview_file.append_column(column_pixbuf)

		self.scrolled_win_select_file.add(self.treeview_file)

	def on_cell_toggled_file(self, widget, path):
		print('on cell toggled file')
		print(path)
		new_val = not self.listfile[path][1]
		self.listfile[path][1] = new_val
		print(self.listfile[path])  # model row
		print(self.listfile[path][1])  # bool: is selected or not ?
		print(self.safer.safe_dirs)

	def on_local_combo_changed(self, combo):
		tree_iter = combo.get_active_iter()
		if tree_iter is not None:
			model = combo.get_model()
			self.local_path = model[tree_iter][0]
			print("Selected local_path: " + self.local_path)

	def on_external_combo_changed(self, combo):
		tree_iter = combo.get_active_iter()
		if tree_iter is not None:
			model = combo.get_model()
			self.external_path = model[tree_iter][0]
			print("Selected external_path: " + self.external_path)
	#
	def compare(self, button):
		# Call by the button
		# TODO : reset self.listfile
		print("compare")
		comparison = self.safer.compare(self.local_path, self.external_path, self.loop)
		print(comparison)
		for filename in comparison['to_copy']:
			self.listfile.append([filename, True, 'edit-copy'])

		for filename in comparison['to_update']:
			self.listfile.append([filename, True, 'system-software-update'])

		for filename in comparison['to_del']:
			self.listfile.append([filename, True, 'edit-delete'])

		self.button_execute.set_sensitive(True)
		self.comparison = comparison

	def execute_compare(self, button):
		print('execute compare')
		results = dict()
		results['to_copy'] = list()
		results['to_update'] = list()
		results['to_del'] = list()
		print(self.comparison['to_copy'])
		for path in range(len(self.listfile)):
			print(self.listfile[path])
			print(self.listfile[path][0])
			print(self.listfile[path][1])
			print(self.listfile[path][2])
			if self.listfile[path][1]:  # is ok ?
				if self.listfile[path][2] == 'edit-copy':
					results['to_copy'].append(self.listfile[path][0])
				if self.listfile[path][2] == 'system-software-update':
					results['to_update'].append(self.listfile[path][0])
				if self.listfile[path][2] == 'edit-delete':
					results['to_del'].append(self.listfile[path][0])

		results['dirs_to_make'] = self.comparison['dirs_to_make']
		results['dirs_to_del'] = self.comparison['dirs_to_del']
		print(results['to_copy'])

		self.safer.execute(results, path_delicate)
		# spinner and timer
		self.button_compare.set_sensitive(True)
		self.button_execute.set_sensitive(False)

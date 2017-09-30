#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio


from .helpers import open_folder


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
		self.local_path = ""
		self.external_path = ""
		button_show_local = Gtk.Button.new_with_label('Ouvrir dossier local')
		button_show_local.connect('clicked', open_folder, self.local_path)
		self.attach(button_show_local, 0, 0, 1, 1)

		button_choose_local = Gtk.Button.new_with_label("Selection du dossier local")
		button_choose_local.connect('clicked', self.on_folder_clicked, True)
		self.attach(button_choose_local, 1, 0, 1, 1)

		self.label_local = Gtk.Label("< selectionner un dossier local >")
		self.attach(self.label_local, 0, 1, 2, 1)

		button_show_external = Gtk.Button.new_with_label('Ouvrir dossier externe')
		button_show_external.connect('clicked', open_folder, self.external_path)
		self.attach(button_show_external, 0, 2, 1, 1)
		# TODO: add little icon to symbolize file explorer
		button_choose_external = Gtk.Button.new_with_label("Selection du dossier externe")
		button_choose_external.connect('clicked', self.on_folder_clicked, False)
		self.attach(button_choose_external, 1, 2, 2, 1)

		self.label_external = Gtk.Label("< selectionner un dossier externe >")
		self.attach(self.label_external, 0, 3, 2, 1)

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
		self.scrolled_win_select_file.set_min_content_height(100)
		self.scrolled_win_select_file.set_max_content_width(600)
		self.scrolled_win_select_file.set_max_content_height(1500)
		self.scrolled_win_select_file.set_hexpand(True)
		self.scrolled_win_select_file.set_vexpand(True)
		self.attach(self.scrolled_win_select_file, 0, 7, 2, 1)

		self.listfile = Gtk.ListStore(bool, str, str)
		self.treeview_file = Gtk.TreeView.new_with_model(self.listfile)

		renderer_toggle = Gtk.CellRendererToggle()
		renderer_toggle.connect("toggled", self.on_cell_toggled_file)
		tree_view_column_toggle = Gtk.TreeViewColumn("Modifier", renderer_toggle, active=0)
		self.treeview_file.append_column(tree_view_column_toggle)

		renderer_text = Gtk.CellRendererText()
		column_text = Gtk.TreeViewColumn("Fichier", renderer_text, text=1)
		self.treeview_file.append_column(column_text)

		renderer_pixbuf = Gtk.CellRendererPixbuf()
		column_pixbuf = Gtk.TreeViewColumn("Image", renderer_pixbuf, icon_name=2)
		self.treeview_file.append_column(column_pixbuf)

		self.scrolled_win_select_file.add(self.treeview_file)

	def on_folder_clicked(self, widget, local=True):
		dialog = Gtk.FileChooserDialog("Selection d'un dossier", self.parent,
			Gtk.FileChooserAction.SELECT_FOLDER,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 "Valider", Gtk.ResponseType.OK))
		dialog.set_default_size(800, 400)

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			filename = dialog.get_filename()
			if local:
				self.local_path = filename
				self.label_local.set_text(filename)
			else:
				self.external_path = filename

				self.label_external.set_text(filename)

		dialog.destroy()

	def on_cell_toggled_file(self, widget, path):
		new_val = not self.listfile[path][0]
		self.listfile[path][0] = new_val

	def compare(self, button):
		"""
		Idées:
			Class action avec path, order (suprimer, copie, couper)
			passe action à execute_compare

		"""
		self.listfile.clear()
		comparison = self.safer.compare(self.local_path, self.external_path)
		for filename in comparison['to_copy']:
			self.listfile.append([True, filename, 'edit-copy'])

		for filename in comparison['to_update']:
			self.listfile.append([True, filename, 'system-software-update'])

		for filename in comparison['to_del']:
			self.listfile.append([True, filename, 'edit-delete'])

		self.button_execute.set_sensitive(True)
		self.comparison = comparison

	def execute_compare(self, button):
		orders = dict()
		orders['dirs_to_make'] = self.comparison['dirs_to_make']  # ~~
		orders['dirs_to_del'] = self.comparison['dirs_to_del']  # ~~
		orders['to_copy'] = list()
		orders['to_update'] = list()
		orders['to_del'] = list()
		for path in range(len(self.listfile)):
			if self.listfile[path][0]:  # is ok ?
				if self.listfile[path][2] == 'edit-copy':
					orders['to_copy'].append(self.listfile[path][1])
				if self.listfile[path][2] == 'system-software-update':
					orders['to_update'].append(self.listfile[path][1])
				if self.listfile[path][2] == 'edit-delete':
					orders['to_del'].append(self.listfile[path][1])

		self.safer.execute(orders, self.local_path, self.external_path)
		# spinner and timer
		self.button_execute.set_sensitive(False)

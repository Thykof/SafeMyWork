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
		button_show_local = Gtk.Button.new_with_label('Dossier local')
		button_show_local.connect('clicked', open_folder, self.local_path)
		self.attach(button_show_local, 0, 0, 1, 1)
		button_show_external = Gtk.Button.new_with_label('Dossier externe')
		button_show_external.connect('clicked', open_folder, self.external_path)
		self.attach(button_show_external, 1, 0, 1, 1)
		# TODO: add little icon to symbolize file explorer

		button_choose_local = Gtk.Button.new_with_label("Selection du dossier local")
		button_choose_local.connect('clicked', self.on_folder_clicked, True)
		self.attach(button_choose_local, 0, 1, 2, 1)

		self.label_local = Gtk.Label("< selectionner un dossier local >")
		self.attach(self.label_local, 0, 2, 2, 1)

		button_choose_external = Gtk.Button.new_with_label("Selection du dossier externe")
		button_choose_external.connect('clicked', self.on_folder_clicked, False)
		self.attach(button_choose_external, 0, 3, 2, 1)

		self.label_external = Gtk.Label("< selectionner un dossier externe >")
		self.attach(self.label_external, 0, 4, 2, 1)

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

	def on_folder_clicked(self, widget, local=True):
		dialog = Gtk.FileChooserDialog("Selection d'un dossier", self.parent,
			Gtk.FileChooserAction.SELECT_FOLDER,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 "Valider", Gtk.ResponseType.OK))
		dialog.set_default_size(800, 400)

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			filename = dialog.get_filename()
			print("Select clicked")
			print("Folder selected: " + filename)
			if local:
				self.local_path = filename
				self.label_local.set_text(filename)
			else:
				self.external_path = filename

				self.label_external.set_text(filename)
		elif response == Gtk.ResponseType.CANCEL:
			print("Cancel clicked")


		dialog.destroy()

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
		"""
		Idées:
			Class action avec path, order (suprimer, copie, couper)
			passe action à execute_compare

		"""
		self.listfile.clear()
		print("compare")
		comparison = self.safer.compare(self.local_path, self.external_path)
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
		orders = dict()
		orders['dirs_to_make'] = self.comparison['dirs_to_make']  # ~~
		orders['dirs_to_del'] = self.comparison['dirs_to_del']  # ~~
		orders['to_copy'] = list()
		orders['to_update'] = list()
		orders['to_del'] = list()
		print(self.comparison)
		for path in range(len(self.listfile)):
			print(self.listfile[path])
			print(self.listfile[path][0])
			print(self.listfile[path][1])
			print(self.listfile[path][2])
			if self.listfile[path][1]:  # is ok ?
				if self.listfile[path][2] == 'edit-copy':
					orders['to_copy'].append(self.listfile[path][0])
				if self.listfile[path][2] == 'system-software-update':
					orders['to_update'].append(self.listfile[path][0])
				if self.listfile[path][2] == 'edit-delete':
					orders['to_del'].append(self.listfile[path][0])

		print(orders)

		self.safer.execute(orders, self.local_path, self.external_path)
		# spinner and timer
		self.button_execute.set_sensitive(False)

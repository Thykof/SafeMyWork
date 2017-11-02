#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

import threading
import asyncio

from .helpers import open_folder as show_dir

class SynchronisationGrid(Gtk.Grid):
	def __init__(self, parent, safer):
		Gtk.Grid.__init__(self)

		# Varaibles
		self.parent = parent
		self.safer = safer
		self.local_path = ''
		self.external_path = ''
		self.loop = asyncio.get_event_loop()
		self.can_execute = False
		self.comparison = None
		self.last_comparison = None
		self.last_comparison

		# Properties
		self.set_column_spacing(5)
		self.set_row_spacing(5)

		# Widgets
		button_show_local = Gtk.Button.new_with_label('Ouvrir dossier local')
		button_show_local.connect('clicked', self.open_folder, True)
		self.attach(button_show_local, 0, 0, 1, 1)

		button_choose_local = Gtk.Button.new_with_label("Selection du dossier local")
		button_choose_local.connect('clicked', self.on_folder_clicked, True)
		self.attach(button_choose_local, 1, 0, 1, 1)

		if self.safer.config['local_path'] == '':
			self.label_local = Gtk.Label("< selectionner un dossier local >")
		else:
			self.label_local = Gtk.Label(self.safer.config['local_path'])
		self.attach(self.label_local, 0, 1, 2, 1)

		button_show_external = Gtk.Button.new_with_label('Ouvrir dossier externe')
		button_show_external.connect('clicked', self.open_folder, False)
		self.attach(button_show_external, 0, 2, 1, 1)
		button_choose_external = Gtk.Button.new_with_label("Selection du dossier externe")
		button_choose_external.connect('clicked', self.on_folder_clicked, False)
		self.attach(button_choose_external, 1, 2, 1, 1)

		if self.safer.config['external_path'] == '':
			self.label_external = Gtk.Label("< selectionner un dossier externe >")
		else:
			self.label_external = Gtk.Label(self.safer.config['external_path'])
		self.attach(self.label_external, 0, 3, 2, 1)

		box = Gtk.Box()
		self.spinner = Gtk.Spinner()
		self.button_compare = Gtk.Button.new_with_label('Comparer')
		self.button_compare.connect('clicked', self.compare)
		self.button_execute = Gtk.Button.new_with_label('Executer')
		self.button_execute.connect('clicked', self.execute_compare)
		box.pack_start(self.button_compare, True, True, 5)
		box.pack_start(self.spinner, True, True, 5)
		box.pack_start(self.button_execute, True, True, 5)
		self.attach(box, 0, 5, 2, 1)

		# List files:
		self.attach(Gtk.Label("Selections des fichiers :"), 0, 6, 3, 1)
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
		self.treeview_file.set_size_request(600, 100)

		self.select_all = Gtk.CheckButton()
		self.select_all.show()
		renderer_toggle = Gtk.CellRendererToggle()
		renderer_toggle.connect("toggled", self.on_cell_toggled_file)
		tree_view_column_toggle = Gtk.TreeViewColumn("", renderer_toggle, active=0)
		tree_view_column_toggle.set_clickable(True)
		tree_view_column_toggle.set_widget(self.select_all)
		tree_view_column_toggle.connect("clicked", self.on_select_all)
		self.treeview_file.append_column(tree_view_column_toggle)

		renderer_text = Gtk.CellRendererText()
		column_text = Gtk.TreeViewColumn("Fichier", renderer_text, text=1)
		column_text.set_expand(True)
		self.treeview_file.append_column(column_text)

		renderer_pixbuf = Gtk.CellRendererPixbuf()
		column_pixbuf = Gtk.TreeViewColumn("", renderer_pixbuf, icon_name=2)
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
		self.listfile[path][0] = not self.listfile[path][0]

	def on_select_all(self, treeviewcolumn):
		self.select_all.set_active(not self.select_all.get_active())
		if self.select_all.get_active():
			for path in range(len(self.listfile)):
				self.listfile[path][0] = True
		else:
			for path in range(len(self.listfile)):
				self.listfile[path][0] = False

	def compare(self, button):
		if self.local_path != "" and self.external_path != '':
			#if not self.thread_compare_active and not self.thread_execute_active:  # No thread are already saving files
			can = True
			for thread in threading.enumerate():
				if thread.name == 'compare' and thread.is_alive():
					can = False
				if thread.name == 'execute_compare' and thread.is_alive():
					can = False

			if can:
				self.parent.info_label.set_text("Comparaison lancé")
				self.treeview_file.hide()
				self.thread = threading.Thread(target=self.do_compare, name="compare")
				self.thread.start()
				self.can_execute = False
		else:
			self.parent.info_label.set_text("Veuillez selectionner des dossiers")
			self.select_all.set_active(False)

	def do_compare(self):
		self.spinner.start()
		self.last_comparison = self.comparison
		self.comparison = self.safer.compare(self.local_path, self.external_path, self.loop)
		self.select_all.set_active(True)
		self.parent.info_label.set_text("Faites vos choix de synchronisation")
		if self.last_comparison != self.comparison:
			self.listfile.clear()
			for filename in self.comparison['to_copy']:
				self.listfile.append([True, filename, 'edit-copy'])

			for filename in self.comparison['to_update']:
				self.listfile.append([True, filename, 'system-software-update'])

			for filename in self.comparison['to_del']:
				self.listfile.append([False, filename, 'edit-delete'])

		self.treeview_file.show()

		self.can_execute = True
		self.spinner.stop()

	def execute_compare(self, button):
		if self.can_execute:
			can = True
			for thread in threading.enumerate():
				if thread.name == 'compare' and thread.is_alive():
					can = False
				if thread.name == 'execute_compare' and thread.is_alive():
					can = False

			if can:
				self.parent.info_label.set_text("Synchronisation lancé")
				self.thread = threading.Thread(target=self.prepare_execute, name='execute_compare')
				self.thread.start()
				self.thread_execute_active = True
				self.can_execute = False
		else:
			self.parent.info_label.set_text("Veuillez d'abord comparer")

	def prepare_execute(self):
		orders = dict()
		orders['dirs_to_make'] = self.comparison['dirs_to_make']  # ~~ it make directories even if no file is copied
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
		self.spinner.start()
		self.safer.execute(orders, self.local_path, self.external_path)
		# here: Erreur de segmentation (core dumped) :
		self.select_all.set_active(False)
		self.parent.info_label.set_text("Synchronisation terminé")
		self.spinner.stop()

	def open_folder(self, button, local):
		if local:
			if self.local_path != '':
				show_dir(None, self.local_path)
			else:
				self.parent.info_label.set_text("Veuillez selectionner un dossier local")
		else:
			if self.external_path != '':
				show_dir(None, self.external_path)
			else:
				self.parent.info_label.set_text("Veuillez selectionner un dossier externe")

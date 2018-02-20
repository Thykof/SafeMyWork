#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib

import asyncio
import json

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
		self.loop = asyncio.get_event_loop()
		self.can_execute = False
		self.comparison = None
		self.last_comparison = None

		# Properties
		self.set_column_spacing(5)
		self.set_row_spacing(5)

		# Widgets
		button_show_local = Gtk.Button.new_with_label('Ouvrir dossier local')
		button_show_local.connect('clicked', self.open_folder, True)
		self.attach(button_show_local, 0, 0, 1, 1)

		button_choose_local = Gtk.Button.new_with_label("Selection du dossier local")
		button_choose_local.connect('clicked', self.select_local)
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

		self.attach(Gtk.Label('Advanced :'), 0, 5, 2, 1)

		box_conf = Gtk.Box()

		self.button_execute = Gtk.Button.new_with_label('Execute')
		self.button_execute.connect('clicked', self.execute_compare)
		box_conf.pack_start(self.button_execute, False, False, 5)

		box_display_results = Gtk.VBox()
		box_display_results.pack_start(Gtk.Label('Display results:'), True, True, 1)
		self.switch_display_results = Gtk.Switch()
		self.switch_display_results.connect('notify::active', self.on_display_res_activate)
		self.switch_display_results.set_active(True)
		box_display_results.pack_start(self.switch_display_results, False, False, 5)
		box_conf.pack_start(box_display_results, True, False, 5)

		box_soft_sync = Gtk.VBox()
		box_soft_sync.pack_start(Gtk.Label('Soft sync:'), True, True, 1)
		switch_soft_sync = Gtk.Switch()
		switch_soft_sync.connect('notify::active', self.on_soft_sync)
		switch_soft_sync.set_active(False)
		box_soft_sync.pack_start(switch_soft_sync, False, False, 5)
		box_conf.pack_start(box_soft_sync, True, False, 5)

		self.attach(box_conf, 0, 6, 2, 1)

		box_analysis = Gtk.Box()
		button_analysis = Gtk.Button.new_with_label('Analyse')
		button_analysis.connect('clicked', self.analyse_folder)
		box_analysis.pack_start(button_analysis, True, False, 5)
		button_compare_analysis = Gtk.Button.new_with_label('Compare from folder analysis')
		button_compare_analysis.connect('clicked', self.on_compare_analysis)
		box_analysis.pack_start(button_compare_analysis, True, False, 5)
		button_show_compare_analysis = Gtk.Button.new_with_label('Show campare analysis')
		button_show_compare_analysis.connect('clicked', self.show_compare_analysis)
		box_analysis.pack_start(button_show_compare_analysis, True, False, 5)
		self.attach(box_analysis, 0, 7, 2, 1)


		# List files:
		self.attach(Gtk.Label("Selections des fichiers :"), 0, 8, 2, 1)
		self.scrolled_win_select_file = Gtk.ScrolledWindow()
		self.scrolled_win_select_file.set_min_content_width(600)
		self.scrolled_win_select_file.set_min_content_height(100)
		self.scrolled_win_select_file.set_max_content_width(600)
		self.scrolled_win_select_file.set_max_content_height(1500)
		self.scrolled_win_select_file.set_hexpand(True)
		self.scrolled_win_select_file.set_vexpand(True)
		self.attach(self.scrolled_win_select_file, 0, 9, 2, 1)

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

	def on_display_res_activate(self, switch, active):
		self.dislay_compare_results = switch.get_active()

	def on_compare_analysis(self, button):
		path1 = folder_chooser(self.parent, False, self.safer.destination, "Local")
		if path1 is None:
			return
		path2 = folder_chooser(self.parent, False, self.safer.destination, "Externe")
		if path2 is not None:
			GLib.idle_add(self.do_compare, path1, path2)

	def on_soft_sync(self, switch, active):
		self.safer.set_soft_sync(switch.get_active())  # safer.soft_sync

	def compare(self, button):
		if self.label_local.get_text() != "" and self.label_external.get_text() != '':
			GLib.idle_add(self.do_compare)
			self.parent.info_label.set_text("Comparaison lancé")
			self.treeview_file.hide()
		else:
			self.parent.info_label.set_text("Veuillez selectionner des dossiers")
			self.select_all.set_active(False)

	def do_compare(self, path1=None, path2=None):
		self.spinner.start()
		self.last_comparison = self.comparison
		if path1 is not None and path2 is not None:  # on compare from analysis
			self.comparison = self.safer.compare_form_files(path1, path2, self.loop)
		else:
			self.comparison = self.safer.compare(self.label_local.get_text(), self.label_external.get_text(), self.loop)

		def compare():
			myscan = scan.Scan()
			files1 = myscan.scan_dir(self.label_local.get_text())
			files2 = myscan.scan_dir(self.label_external.get_text())
			self.mysync = sync.Sync(self.label_local.get_text(), self.label_external.get_text())
			return self.mysync.compare(files1, files2)
		self.comparison_ = compare()
		self.select_all.set_active(True)
		self.parent.info_label.set_text("Faites vos choix de synchronisation")
		self.show_compare_results()  # use self.comparison
		self.treeview_file.show()
		self.can_execute = True
		self.spinner.stop()

	def show_compare_results(self, comparison=None):
		# Called by do_compare or show_compare_analysis
		if not self.dislay_compare_results:
			self.listfile.clear()
		else:
			if comparison is not None:
				self.comparison = comparison
			#if self.last_comparison != self.comparison:  # disable the feature because of switch display results
			self.listfile.clear()
			if not self.safer.soft_sync:  # Deep sync, show ConflictDialog
				if len(self.comparison_['conflicts']) > 0:
					conflict_dialog = ConflictDialog(self.parent, self.comparison_)
					response = conflict_dialog.run()
					if response == Gtk.ResponseType.OK:
						conflict_dialog.destroy()
						orders = conflict_dialog.comparison
						confirm_dialog = ConfirmDialog(self.parent, orders)
						response = confirm_dialog.run()
						if response == Gtk.ResponseType.OK:
							confirm_dialog.destroy()
							# execute sync
							GLib.idle_add(self.mysync.sync, orders)
						else:
							confirm_dialog.destroy()
							self.parent.info_label.set_text("Sync aborted")
					else:
						conflict_dialog.destroy()
				else:
					GLib.idle_add(self.mysync.sync, self.comparison_)
					self.parent.info_label.set_text("Done")
			else:  # Soft sync
				for filename in self.comparison['to_copy']:
					self.listfile.append([True, filename, 'edit-copy'])

				for filename in self.comparison['to_update']:
					self.listfile.append([True, filename, 'system-software-update'])

				for filename in self.comparison['to_del']:
					self.listfile.append([False, filename, 'edit-delete'])

	def execute_compare(self, button):
		if self.can_execute:
			self.spinner.start()
			GLib.idle_add(self.prepare_execute)
			self.parent.info_label.set_text("Synchronisation lancé")
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
		self.safer.execute(orders, self.label_local.get_text(), self.label_external.get_text())
		self.select_all.set_active(False)
		self.parent.info_label.set_text("Synchronisation terminé")
		self.spinner.stop()

	def analyse_folder(self, button, loop=None):
		folder = folder_chooser(self.parent)
		if folder:
			if loop is None:
				loop = asyncio.get_event_loop()
			loop.run_until_complete(self.safer.get_to_save(folder))

	def show_compare_analysis(self, button):
		filename = folder_chooser(self.parent, False, self.safer.destination)
		if filename:
			if 'compare' in filename and filename[-5:] == '.json':
				with open(filename, 'r') as myfile:
					comparison = json.loads(myfile.read())
				self.show_compare_results(comparison)

	def open_folder(self, button, local):
		if local:
			if self.label_local.get_text() != '':
				show_dir(None, self.label_local.get_text())
			else:
				self.parent.info_label.set_text("Veuillez selectionner un dossier local")
		else:
			if self.label_external.get_text() != '':
				show_dir(None, self.label_external.get_text())
			else:
				self.parent.info_label.set_text("Veuillez selectionner un dossier externe")

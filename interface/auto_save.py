#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

import asyncio
from time import time
from os import path
import threading

from .helpers import open_folder

class AutoSavingGrid(Gtk.Grid):
	"""The first page of the notebook."""
	def __init__(self, safer):
		Gtk.Grid.__init__(self)
		# Variables
		self.safer = safer
		self.thread = None
		self.timer = None
		self.scan_time = None
		self.state = 'copy'
		self.loop = asyncio.get_event_loop()
		# Properties
		self.set_column_spacing(5)
		self.set_row_spacing(5)
		# Widgets
		button_show_saved = Gtk.Button.new_with_label('Fichiers sauvés')
		button_show_saved.connect('clicked', open_folder, self.safer.config['safe_dir'])
		self.attach(button_show_saved, 0, 0, 1, 1)

		button_scan_now = Gtk.Button.new_with_label('Scanner maintenant')
		button_scan_now.connect('clicked', self.scan_now)
		self.attach(button_scan_now, 1, 0 , 1, 1)

		self.text = Gtk.Label('En attente...')
		self.switch_auto_save = Gtk.Switch()
		self.switch_auto_save.connect('notify::active', self.on_switch_activate)
		self.switch_auto_save.set_active(False)
		self.spinner = Gtk.Spinner()
		hbox1 = Gtk.Box(spacing=6)
		hbox1.pack_start(self.text, True, True, 0)
		hbox1.pack_start(self.switch_auto_save, True, True, 0)
		hbox1.pack_start(self.spinner, True, True, 0)
		self.attach(hbox1, 0, 1, 2, 1)
		self.switch_auto_save.do_grab_focus(self.switch_auto_save)

		hbox2 = Gtk.Box(spacing=6)
		button1 = Gtk.RadioButton.new_with_label_from_widget(None, "Copier")
		button1.connect("toggled", self.on_button_toggled, "copy")
		hbox2.pack_start(button1, False, False, 0)
		button2 = Gtk.RadioButton.new_from_widget(button1)
		button2.set_label("MAJ")
		button2.connect("toggled", self.on_button_toggled, "maj")
		hbox2.pack_start(button2, False, False, 0)
		button3 = Gtk.RadioButton.new_with_mnemonic_from_widget(button1, "Filtrer")
		button3.connect("toggled", self.on_button_toggled, "filter")
		hbox2.pack_start(button3, False, False, 0)
		self.attach(hbox2, 0, 2, 2, 1)

		# TreeView
		label_select_folder = Gtk.Label("Selection des dossiers :")
		self.attach(label_select_folder, 0, 3, 2, 1)
		self.scrolled_win_select_folder = Gtk.ScrolledWindow()
		self.attach(self.scrolled_win_select_folder, 0, 4, 2, 1)

		self.listselect = Gtk.ListStore(str, bool)
		for path_delicate, safe_path in self.safer.safe_dirs.items():
			# safe_path is useless here, path_delicate is the source
			self.listselect.append([path_delicate, safe_path['activate']])

		self.treeview_select = Gtk.TreeView.new_with_model(self.listselect)
		cell_renderer_text = Gtk.CellRendererText()
		tree_view_column_text = Gtk.TreeViewColumn("Dossier", cell_renderer_text, text=0)
		self.treeview_select.append_column(tree_view_column_text)
		cell_renderer_toggle = Gtk.CellRendererToggle()
		cell_renderer_toggle.set_radio(True)
		cell_renderer_toggle.connect("toggled", self.on_cell_toggled_select)
		tree_view_column_toggle = Gtk.TreeViewColumn("Scanner", cell_renderer_toggle, active=1)
		self.treeview_select.append_column(tree_view_column_toggle)
		self.scrolled_win_select_folder.add(self.treeview_select)

		self.entry = Gtk.Entry()
		self.attach(self.entry, 0, 5, 2, 1)

		button_add_watched = Gtk.Button.new_with_label('Ajouter')
		button_add_watched.connect('clicked', self.add_delicate_dir)
		self.attach(button_add_watched, 0, 6, 1, 1)

		button_del_watched = Gtk.Button.new_with_label('Supprimer')
		button_del_watched.connect('clicked', self.del_delicate_dir)
		self.attach(button_del_watched, 1, 6, 1, 1)

	def on_switch_activate(self, switch, active):
		"""This start or stop perpetual scan."""
		if switch.get_active():
			self.start_scan()
		else:
			self.stop_watching()

	def on_button_toggled(self, button, name):
		# Radio buttons for copy, update or filter
		if button.get_active():
			self.state = name

	def on_cell_toggled_select(self, widget, path):
		print(widget)
		print(self.listselect)
		print(path)
		print(self.listselect[path])  # model row
		new_val = not self.listselect[path][1]
		self.listselect[path][1] = new_val
		self.safer.safe_dirs[self.listselect[path][0]]['activate'] = new_val
		print(new_val)
		print(self.safer.safe_dirs)
	#
	def scan_now(self, *args):  # start the thread
		"""Make thread, that scan and copy files, if no one is already started.
		Call by the button or by start_scan."""
		can = True
		for thread in threading.enumerate():
			if thread.name == 'scan' and thread.is_alive():
					can = False
		if can:  # No thread are already saving files
			self.thread = threading.Thread(target=self.execute, name='scan')
			self.thread.start()

	def execute(self):  # target of thread
		"""Call by a thread in `scan_now`, run `Safer`."""
		self.spinner.start()
		self.text.set_text('Scan en cours')
		begin = time()
		if self.state == 'copy':
			self.safer.copy_files()
		elif self.state == 'filter':
			self.safer.save_with_filters(loop=self.loop)
		elif self.state == 'maj':
			self.safer.update(loop=self.loop)

		end = time()
		self.scan_time = round(end - begin, 2)
		self.spinner.stop()
		self.text.set_text('Scanné en ' + str(self.scan_time) + ' s')

	def start_scan(self):  # perpetual scan
		"""Run `scan_now`, start a timer thread to itself for perpetual scan.
		Call by the switch."""
		self.text.set_text('Surveillance active')
		self.scan_now()
		self.timer = threading.Timer(self.safer.config['timedelta']*10, self.start_scan)
		self.timer.start()

	def stop_watching(self):
		"""Cancel timer thread. Call by the switch."""
		if self.timer.is_alive():
			self.timer.cancel()
			self.timer.join()
		self.text.set_text('En attente...')
		# TODO:Cherche un thread de copy en cours de traitement et indoquer que ça va se finir mais que ça continue

	def add_delicate_dir(self, button):
		"""Add a dirctory to scan."""
		new_dir = self.entry.get_text()
		if new_dir != '' and new_dir not in self.safer.config['delicate_dirs'] and path.exists(new_dir):
			self.safer.add_delicate_dir(new_dir)
			self.text.set_text('Dossier ajouté')

	def del_delicate_dir(self, button):
		"""Remove a directory to scan."""
		pass
		# open a dial to select the delicate forlder to delete

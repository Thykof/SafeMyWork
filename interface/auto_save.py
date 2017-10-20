#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

import asyncio
from time import time
from os import path
import threading

from .helpers import open_folder
from .dialog import DelDirDialog

class AutoSavingGrid(Gtk.Grid):
	"""The first page of the notebook."""
	def __init__(self, parent, safer):
		Gtk.Grid.__init__(self)
		# Variables
		self.parent = parent
		self.safer = safer
		self.thread = None
		self.timer = None
		self.scan_time = None
		self.state = 'Copier'
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

		button_timedelta = Gtk.Button.new_with_label('Valider')
		button_timedelta.connect('clicked', self.on_changed_timedelta)

		adjustment = Gtk.Adjustment(10, 1, 60, 10, 10, 0)
		self.spinbutton = Gtk.SpinButton(adjustment=adjustment)
		self.spinbutton.connect('change-value', self.on_changed_timedelta)
		self.spinbutton.set_digits(0)
		self.spinbutton.set_value(self.safer.config['timedelta'])

		hbox1 = Gtk.Box(spacing=6)
		hbox1.pack_start(self.text, True, True, 0)
		hbox1.pack_start(self.switch_auto_save, True, True, 0)
		hbox1.pack_start(self.spinner, True, True, 0)
		hbox1.pack_start(Gtk.Label('Délai (min) :'), True, True, 0)
		hbox1.pack_start(self.spinbutton, True, True, 0)
		hbox1.pack_start(button_timedelta, True, True, 0)
		self.attach(hbox1, 0, 1, 2, 1)
		self.switch_auto_save.do_grab_focus(self.switch_auto_save)

		hbox2 = Gtk.Box(spacing=6)
		button1 = Gtk.RadioButton.new_with_label_from_widget(None, "Copier")
		button1.set_hexpand(True)
		button1.connect("toggled", self.on_button_toggled, "Copier")
		hbox2.pack_start(button1, False, False, 0)
		button2 = Gtk.RadioButton.new_from_widget(button1)
		button2.set_hexpand(True)
		button2.set_label("MAJ")
		button2.connect("toggled", self.on_button_toggled, "maj")
		hbox2.pack_start(button2, False, False, 0)
		button3 = Gtk.RadioButton.new_with_mnemonic_from_widget(button1, "Filtrer")
		button3.set_hexpand(True)
		button3.connect("toggled", self.on_button_toggled, "Filtrer")
		hbox2.pack_start(button3, False, False, 0)
		self.attach(hbox2, 0, 2, 2, 1)

		# TreeView
		label_select_folder = Gtk.Label("Dossiers sous surveillance :")
		label_select_folder.set_hexpand(True)
		self.attach(label_select_folder, 0, 3, 2, 1)

		self.scrolledwin_delicate = Gtk.ScrolledWindow()
		self.scrolledwin_delicate.set_min_content_height(100)
		self.attach(self.scrolledwin_delicate, 0, 4, 2, 1)

		self.list_delicate = Gtk.ListStore(str)
		for path_delicate in self.safer.delicate_dirs:
			self.list_delicate.append([path_delicate])

		treeview = Gtk.TreeView(model=self.list_delicate)

		renderer_text = Gtk.CellRendererText()
		column_text = Gtk.TreeViewColumn("Chemin", renderer_text, text=0)
		treeview.append_column(column_text)

		self.scrolledwin_delicate.add(treeview)

		button_add_watched = Gtk.Button.new_with_label('Ajouter')
		button_add_watched.connect('clicked', self.add_delicate_dir)
		self.attach(button_add_watched, 0, 5, 1, 1)

		button_del_watched = Gtk.Button.new_with_label('Supprimer')
		button_del_watched.connect('clicked', self.del_delicate_dir)
		self.attach(button_del_watched, 1, 5, 1, 1)

	def on_switch_activate(self, switch, active):
		"""This start or stop perpetual scan."""
		if switch.get_active():
			self.start_scan()
		else:
			self.stop_watching()

	def on_button_toggled(self, button, name):
		"""Radio buttons for copy, update or filter"""
		if button.get_active():
			self.state = name
			self.parent.info_label.set_text("Changement du mode : " + name)

	def on_changed_timedelta(self, button):
		timedelta = int(self.spinbutton.get_value())
		self.safer.config['timedelta'] = timedelta
		message = "Delai changé : " + str(timedelta)
		message += " minutes" if timedelta > 1 else " minute"
		self.parent.info_label.set_text(message)

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
		self.parent.info_label.set_text('Scan en cours')
		begin = time()
		if self.state == 'Copier':
			self.safer.copy_files()
		elif self.state == 'Filtrer':
			self.safer.save_with_filters(loop=self.loop)
		elif self.state == 'maj':
			self.safer.update(loop=self.loop)

		"""
		(main.py:6313): Pango-CRITICAL **: pango_layout_get_line_count: assertion 'layout != NULL' failed
		(main.py:6313): Pango-CRITICAL **: pango_layout_get_pixel_extents: assertion 'PANGO_IS_LAYOUT (layout)' failed
		"""

		end = time()
		self.scan_time = round(end - begin, 2)
		self.spinner.stop()
		self.parent.info_label.set_text('Scanné en ' + str(self.scan_time) + ' s')

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
		# TODO:Cherche un thread de copy en cours de traitement et indiquer que ça va se finir mais que ça continue

	def add_delicate_dir(self, button):
		"""Add a dirctory to scan."""
		dialog = Gtk.FileChooserDialog("Selection d'un dossier à surveiller", self.parent,
			Gtk.FileChooserAction.SELECT_FOLDER,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 "Valider", Gtk.ResponseType.OK))
		dialog.set_default_size(800, 400)

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			dirname = dialog.get_filename()
			if dirname != '' and dirname not in self.safer.delicate_dirs:
				self.list_delicate.append([dirname])
				self.safer.add_delicate_dir(dirname)
				self.parent.info_label.set_text("Dossier ajouté")
			else:
				self.parent.info_label.set_text("Dossier invalide")

		dialog.destroy()

	def del_delicate_dir(self, button):
		"""Remove a directory to scan."""
		if len(self.list_delicate) != 0:
			dialog = DelDirDialog(self.parent, self.list_delicate)
			response = dialog.run()
			if response == Gtk.ResponseType.OK:
				if dialog.dirname is not None and dialog.diriter is not None:
					self.safer.del_delicate_dir(dialog.dirname)
					self.list_delicate.remove(dialog.diriter)
					self.parent.info_label.set_text("Dossier supprimé")
			dialog.destroy()
		else:
			self.parent.info_label.set_text("Rien à supprimer")

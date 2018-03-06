#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import asyncio
from time import time
import threading

from .helpers import open_folder
from .dialogs.dialog import DelDirDialog
from .thread import Thread

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
		self.state = 'Copy'
		self.loop = asyncio.get_event_loop()
		# Properties
		self.set_column_spacing(5)
		self.set_row_spacing(5)
		# Widgets
		button_show_saved = Gtk.Button.new_with_label('Safe folders')
		#button_show_saved.connect('clicked', open_folder, self.safer.destination)
		button_show_saved.connect('clicked', self.on_show_saved)
		self.attach(button_show_saved, 0, 0, 1, 1)

		button_scan_now = Gtk.Button.new_with_label('Scan now')
		button_scan_now.connect('clicked', self.scan_now)
		self.attach(button_scan_now, 1, 0 , 1, 1)

		self.text = Gtk.Label('Waiting...')
		self.switch_auto_save = Gtk.Switch()
		self.switch_auto_save.connect('notify::active', self.on_switch_activate)
		self.switch_auto_save.set_active(False)
		self.spinner = Gtk.Spinner()

		button_timedelta = Gtk.Button.new_with_label('Validate')
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
		hbox1.pack_start(Gtk.Label('Period (min):'), True, True, 0)
		hbox1.pack_start(self.spinbutton, True, True, 0)
		hbox1.pack_start(button_timedelta, True, True, 0)
		self.attach(hbox1, 0, 1, 2, 1)
		self.switch_auto_save.do_grab_focus(self.switch_auto_save)

		hbox2 = Gtk.Box(spacing=6)
		button1 = Gtk.RadioButton.new_with_label_from_widget(None, "Copy")
		button1.set_hexpand(True)
		button1.connect("toggled", self.on_button_toggled, "Copy")
		hbox2.pack_start(button1, False, False, 0)
		button2 = Gtk.RadioButton.new_from_widget(button1)
		button2.set_hexpand(True)
		button2.set_label("Update")
		button2.connect("toggled", self.on_button_toggled, "Update")
		hbox2.pack_start(button2, False, False, 0)
		button3 = Gtk.RadioButton.new_with_mnemonic_from_widget(button1, "Filter")
		button3.set_hexpand(True)
		button3.connect("toggled", self.on_button_toggled, "Filter")
		hbox2.pack_start(button3, False, False, 0)
		self.attach(hbox2, 0, 2, 2, 1)

		# TreeView
		label_select_folder = Gtk.Label("Folders watched:")
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
		column_text = Gtk.TreeViewColumn("Path", renderer_text, text=0)
		treeview.append_column(column_text)

		self.scrolledwin_delicate.add(treeview)

		button_add_watched = Gtk.Button.new_with_label('Add')
		button_add_watched.connect('clicked', self.add_delicate_dir)
		self.attach(button_add_watched, 0, 5, 1, 1)

		button_del_watched = Gtk.Button.new_with_label('Del')
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
			self.parent.info_label.set_text("Select mode: " + name)

	def on_changed_timedelta(self, button):
		timedelta = int(self.spinbutton.get_value())
		self.safer.config['timedelta'] = timedelta
		message = "Period changed: " + str(timedelta)
		message += " minutes" if timedelta > 1 else " minute"
		self.parent.info_label.set_text(message)

	def on_show_saved(self, button):
		open_folder(self.safer.destination)

	def scan_now(self, *args):  # start the thread
		"""Make thread, that scan and copy files, if no one is already started.
		Call by the button or by start_scan."""
		can = True
		for thread in threading.enumerate():
			if thread.name == 'scan' and thread.is_alive():
					can = False
		if can:  # No thread are already saving files
			self.thread = Thread(self.execute, self.after_execute, name='scan')
			self.thread.start()

	def execute(self):  # target of thread
		"""Call by a thread in `scan_now`, run `Safer`."""
		self.spinner.start()
		self.parent.info_label.set_text('Scan runing')
		self.begin = time()
		if self.state == 'Copy':
			self.error = self.safer.copy_files()
		elif self.state == 'Filter':
			self.error = self.safer.save_with_filters(loop=self.loop)
		elif self.state == 'Update':
			self.error = self.safer.update(loop=self.loop)

	def after_execute(self):
		self.spinner.stop()
		end = time()
		self.scan_time = round(end - self.begin, 2)
		self.parent.info_label.set_text('Scaned in ' + str(self.scan_time) + ' s')

		if len(self.error) > 0:
			dialog = Gtk.MessageDialog(self.parent, 0, Gtk.MessageType.INFO,
				Gtk.ButtonsType.OK, "Limit size reached, abort")
			msg = ''
			for folder in self.error:
				msg += folder + '\n'
			dialog.format_secondary_text(
				msg + "One of these folder is more than 3 Go.")
			dialog.run()
			dialog.destroy()

	def start_scan(self):  # perpetual scan
		"""Run `scan_now`, start a timer thread to itself for perpetual scan.
		Call by the switch."""
		self.text.set_text('Watching activate')
		self.scan_now()
		self.timer = threading.Timer(self.safer.config['timedelta']*10, self.start_scan)
		self.timer.start()

	def stop_watching(self):
		"""Cancel timer thread. Call by the switch."""
		if self.timer.is_alive():
			self.timer.cancel()
			self.timer.join()
		self.text.set_text('Waiting...')
		# TODO:Cherche un thread de copy en cours de traitement et indiquer que ça va se finir mais que ça continue

	def add_delicate_dir(self, button):
		"""Add a dirctory to scan."""
		dialog = Gtk.FileChooserDialog("Select a folder to watch", self.parent,
			Gtk.FileChooserAction.SELECT_FOLDER,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 "Validate", Gtk.ResponseType.OK))
		dialog.set_default_size(800, 400)

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			dirname = dialog.get_filename()
			if dirname != '' and dirname not in self.safer.delicate_dirs and dirname != self.safer.destination:
				self.list_delicate.append([dirname])
				self.safer.add_delicate_dir(dirname)
				self.parent.info_label.set_text("Folder added")
			else:
				self.parent.info_label.set_text("Invalid folder")

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
					self.parent.info_label.set_text("Folder deleted")
			dialog.destroy()
		else:
			self.parent.info_label.set_text("Nothing to delete")

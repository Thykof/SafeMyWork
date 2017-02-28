# -*- coding: utf-8 -*-
#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import threading
from os import path
from platform import system

from .menubar import create_menus
from .tools import about, MainGrid
from .dialog import del_dir_dialog, Settings_dial
from watcher.watcher import Watcher
import watcher
from watcher.safe import Safer

SYSTEM = system()
if SYSTEM == 'Linux':
	from subprocess import Popen
elif SYSTEM == 'Windows':
	from os import startfile
else:
	watcher.mod.tell('Import Error')

class MyWindow(Gtk.ApplicationWindow):
	def __init__(self, app):
		Gtk.Window.__init__(self, title='SafeMyWork 1.0', application=app)
		self.set_position(Gtk.WindowPosition.CENTER)
		self.set_border_width(5)

		self.grid = MainGrid(self)
		self.add(self.grid)
		self.grid.switch_start.do_grab_focus(self.grid.switch_start)

		create_menus(self)

		self.safer = Safer()
		self.time_delta = .5
		self.timer = None
		self.thread = None

		self.initialize_config()

	def initialize_config(self):
		for watched_dir in self.safer.config['delicate_dirs']:
			self.grid.watched_list.append_text(watched_dir)

	def save_config(self):
		self.safer.save_config()

	def watch(self, loop):
		"""Launch watch"""
		self.grid.spinner.start()
		self.safer.update()
		self.grid.spinner.stop()
		if loop:
			self.timer = threading.Timer(self.time_delta*60, self.start_watching, args=(loop,))
			self.timer.start()

	def start_watching(self, loop):
		"""Start watching : watch + timer"""
		can = True
		if loop:
			can = self.grid.switch_start.get_active()
		for thread in threading.enumerate():
			if thread.name == 'watcher_loop' or thread.name == 'watcher_alone':
				if thread.is_alive():
					can = False
		if can:
			self.thread = threading.Thread(target=self.watch, name='watcher_loop', args=(loop,))
			self.thread.start()
			if loop:
				self.grid.text.set_text('Surveillance active')

	def stop_watching(self):
		"""Cancel timer"""
		if self.timer is not None:
			self.timer.cancel()
			self.grid.text.set_text('En attente...')

	def abort_watch(self):
		"""Abort current watch"""
		pass

	def show_saved(self, *args):
		if SYSTEM == 'Linux':
			Popen(['xdg-open', self.safer.config['safe_dir']])
		elif SYSTEM == 'Windows':
			startfile(self.safer.config['safe_dir'])

	def settings(self, action, parameter):
		dialog_settings = Settings_dial(self)
		dialog_settings.run()

	def add_watched_dir(self, button):
		tree_iter = self.grid.watched_list.get_active_iter()
		if tree_iter is None:
			new_dir = self.grid.watched_list.get_child().get_text()
			if new_dir != '' and new_dir not in self.safer.config['delicate_dirs'] and path.exists(new_dir):
				self.grid.watched_list.append_text(new_dir)
				self.safer.add_delicate_dir(new_dir)
				self.grid.text.set_text('Dossier ajouté')

	def del_watched_dir(self, button):
		tree_iter = self.grid.watched_list.get_active_iter()
		if tree_iter is not None:
			model = self.grid.watched_list.get_model()
			directory = model[tree_iter][0]
			must_del, dialog = del_dir_dialog(self, directory)
			dialog.destroy()
			if must_del:
				self.safer.del_delicate_dir(directory)
				self.grid.watched_list.remove(int(self.grid.watched_list.get_active()))
				self.grid.text.set_text('Dossier supprimé')

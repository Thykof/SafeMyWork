# -*- coding: utf-8 -*-
#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
import threading
from os import path
from platform import system

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

		self.safer = Safer()
		self.time_delta = .5
		self.timer = None
		self.thread = None

		self.grid = Gtk.Grid()
		self.grid.set_column_spacing(5)
		self.grid.set_row_spacing(5)

		button_show_saved = Gtk.Button.new_with_label('Fichiers sauvés')
		button_show_saved.connect('clicked', self.show_saved)
		self.grid.attach(button_show_saved, 0, 0, 1, 1)

		button_check_now = Gtk.Button.new_with_label('Scanner maintenant')
		button_check_now.connect('clicked', lambda arg: self.start_watching(False))
		self.grid.attach(button_check_now, 1, 0 , 1, 1)

		self.text = Gtk.Label('En attente...')
		self.switch_start = Gtk.Switch()
		self.switch_start.connect('notify::active', self.on_switch_activated)
		self.switch_start.set_active(False)
		self.switch_start.do_grab_focus(self.switch_start)
		self.spinner = Gtk.Spinner()
		hbox = Gtk.Box(spacing=6)
		hbox.pack_start(self.text, True, True, 0)
		hbox.pack_start(self.switch_start, True, True, 0)
		hbox.pack_start(self.spinner, True, True, 0)
		self.grid.attach(hbox, 0, 1, 2, 1)

		self.watched_list = Gtk.ComboBoxText.new_with_entry()
		button_add_watched = Gtk.Button.new_with_label('Ajouter')
		button_add_watched.connect('clicked', self.add_watched_dir)
		button_del_watched = Gtk.Button.new_with_label('Supprimer')
		button_del_watched.connect('clicked', self.del_watched_dir)		
		self.grid.attach(self.watched_list, 0, 2, 2, 1)
		self.grid.attach(button_add_watched, 0, 3, 1, 1)
		self.grid.attach(button_del_watched, 1, 3, 1, 1)

		self.add(self.grid)

		# Menubar
		show_saved_action = Gio.SimpleAction.new('show_saved')
		show_saved_action.connect('activate', self.show_saved)
		self.add_action(show_saved_action)

		settings_action = Gio.SimpleAction.new('settings')
		settings_action.connect('activate', self.settings)
		self.add_action(settings_action)

		start_watching_action = Gio.SimpleAction.new('start_watching')
		start_watching_action.connect('activate', self.start_watching, False)
		self.add_action(start_watching_action)

		stop_watching_action = Gio.SimpleAction.new('stop_watching')
		stop_watching_action.connect('activate', self.stop_watching)
		self.add_action(stop_watching_action)

		watch_now_action = Gio.SimpleAction.new('watch_now')
		watch_now_action.connect('activate', self.start_watching, False)
		self.add_action(watch_now_action)

		about_action = Gio.SimpleAction.new('about')
		about_action.connect('activate', self.about)
		self.add_action(about_action)

		# Initialize config
		for watched_dir in self.safer.config['delicate_dirs']:
			self.watched_list.append_text(watched_dir)

	def on_switch_activated(self, switch, active):
		print(active)
		if switch.get_active():
			self.start_watching(True)
		else:
			self.stop_watching()

	def save_config(self):
		self.safer.save_config()

	def watch(self, loop):
		"""Launch watch"""
		self.spinner.start()
		self.safer.update()
		self.spinner.stop()
		if loop:
			self.timer = threading.Timer(self.time_delta*60, self.start_watching, args=(loop,))
			self.timer.start()

	def start_watching(self, loop, *args):
		"""Start watching : watch + timer"""
		can = True
		if loop:
			can = self.switch_start.get_active()

		for thread in threading.enumerate():
			if thread.name == 'watcher_loop' or thread.name == 'watcher_alone':
				if thread.is_alive():
					can = False
		if can:
			if not self.switch_start.get_active():
				self.switch_start.set_active(True)
			self.thread = threading.Thread(target=self.watch, name='watcher_loop', args=(loop,))
			self.thread.start()
			if loop:
				self.text.set_text('Surveillance active')

	def stop_watching(self, *args):
		"""Cancel timer"""
		if self.switch_start.get_active():
				self.switch_start.set_active(False)
		if self.timer is not None:
			self.timer.cancel()
			self.text.set_text('En attente...')

	def abort_watch(self):
		"""Abort current watch"""
		if self.timer is not None:
			self.timer.cancel()

	def show_saved(self, button):
		if SYSTEM == 'Linux':
			Popen(['xdg-open', self.safer.config['safe_dir']])
		elif SYSTEM == 'Windows':
			startfile(self.safer.config['safe_dir'])

	def settings(self, action, parameter):
		dialog_settings = Settings_dial(self)
		dialog_settings.run()

	def add_watched_dir(self, button):
		tree_iter = self.watched_list.get_active_iter()
		if tree_iter is None:
			new_dir = self.watched_list.get_child().get_text()
			if new_dir != '' and new_dir not in self.safer.config['delicate_dirs'] and path.exists(new_dir):
				self.watched_list.append_text(new_dir)
				self.safer.add_delicate_dir(new_dir)
				self.text.set_text('Dossier ajouté')

	def del_watched_dir(self, button):
		tree_iter = self.watched_list.get_active_iter()
		if tree_iter is not None:
			model = self.watched_list.get_model()
			directory = model[tree_iter][0]
			must_del, dialog = del_dir_dialog(self, directory)
			dialog.destroy()
			if must_del:
				self.safer.del_delicate_dir(directory)
				self.watched_list.remove(int(self.watched_list.get_active()))
				self.text.set_text('Dossier supprimé')

	def about(self, action):
		about_dialog = Gtk.AboutDialog(transient_for=self)
		about_dialog.set_program_name('SafeMyWork')
		about_dialog.set_version('1.0')
		about_dialog.set_website('https://github.com/Thykof/SafeMyWork')
		about_dialog.set_website_label("Github")
		about_dialog.set_authors(['Nathan Seva'])
		about_dialog.set_comments('Utilitaire SafeMyWork')
		about_dialog.set_license('SafeMyWork est sous la license GNU GPL(v3). \n\n https://github.com/Thykof/SafeMyWork/blob/master/LICENSE')

		about_dialog.run()
		about_dialog.destroy()

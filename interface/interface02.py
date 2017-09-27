#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
import threading
from os import path
from time import time, sleep
import asyncio
from platform import system
SYSTEM = system()
if SYSTEM == 'Linux':
	from subprocess import Popen
elif SYSTEM == 'Windows':
	from os import startfile
else:
	print('Import Error')


from .dialog import del_dir_dialog, Settings_dial
from safer.safe import Safer
from safer.helpers import set_order_file

class MyWindow(Gtk.ApplicationWindow):
	"""Application."""
	def __init__(self, app):
		Gtk.Window.__init__(self, title='SafeMyWork 1.0', application=app)
		self.set_position(Gtk.WindowPosition.CENTER)
		self.set_border_width(5)

		self.loop = asyncio.get_event_loop()

		self.safer = Safer(items={'timedelta': .5})
		self.timer = None
		self.scan_time = None
		self.state = 'copy'
		self.thread = None
		self.callback = Gio.SimpleAction.new('callback_info')
		self.callback.connect('activate', self.dialog_info)
		self.add_action(self.callback)

		# Main grid
		self.grid = Gtk.Grid()
		self.grid.set_column_spacing(5)
		self.grid.set_row_spacing(5)

		button_show_saved = Gtk.Button.new_with_label('Fichiers sauvés')
		button_show_saved.connect('clicked', self.show_saved)
		self.grid.attach(button_show_saved, 0, 0, 1, 1)

		button_check_now = Gtk.Button.new_with_label('Scanner maintenant')
		button_check_now.connect('clicked', self.scan_now)
		self.grid.attach(button_check_now, 1, 0 , 1, 1)

		self.text = Gtk.Label('En attente...')
		self.switch_start = Gtk.Switch()
		self.switch_start.connect('notify::active', self.on_switch_activate)
		self.switch_start.set_active(False)
		self.spinner = Gtk.Spinner()
		hbox1 = Gtk.Box(spacing=6)
		hbox1.pack_start(self.text, True, True, 0)
		hbox1.pack_start(self.switch_start, True, True, 0)
		hbox1.pack_start(self.spinner, True, True, 0)
		self.grid.attach(hbox1, 0, 1, 2, 1)
		self.switch_start.do_grab_focus(self.switch_start)

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
		self.grid.attach(hbox2, 0, 2, 2, 1)

		self.watched_list = Gtk.ComboBoxText.new_with_entry()
		button_add_watched = Gtk.Button.new_with_label('Ajouter')
		button_add_watched.connect('clicked', self.add_watched_dir)
		button_del_watched = Gtk.Button.new_with_label('Supprimer')
		button_del_watched.connect('clicked', self.del_watched_dir)
		self.grid.attach(self.watched_list, 0, 3, 2, 1)
		self.grid.attach(button_add_watched, 0, 4, 1, 1)
		self.grid.attach(button_del_watched, 1, 4, 1, 1)

		label_sync = Gtk.Label("Synchronisation :")
		self.grid.attach(label_sync, 0, 5, 2, 1)
		# Select delicate folders:
		# Dans le tableau : ajouter les boutons supprimer et modifier
		# Dernière ligne du tableau : ajouter un chemin
		label_select_folder = Gtk.Label("Selection des dossiers :")
		self.grid.attach(label_select_folder, 0, 6, 2, 1)
		select_box = Gtk.VBox(spacing=6)
		i = 1
		pre_widget = None
		self.radio_delicate = dict()
		for path_delicate, safe_path in self.safer.safe_dirs.items():
			self.radio_delicate[path_delicate] = Gtk.RadioButton.new_with_label_from_widget(pre_widget, path_delicate)
			button.connect("toggled", self.on_button_select_toggled, str(i))
			i += 1
			pre_widget = button
			select_box.pack_start(button, False, False, 0)

		self.grid.attach(select_box, 0, 7, 2, 1)

		# List files:
		label_select_files = Gtk.Label("Selections des fichiers :")
		self.grid.attach(label_select_files, 0, 8, 2, 1)
		self.scrolled_win_select_file = Gtk.ScrolledWindow()
		self.grid.attach(self.scrolled_win_select_file, 0, 9, 2, 1)

		self.listfile = Gtk.ListStore(str, str, bool)
		self.treeview_file = Gtk.TreeView.new_with_model(self.listfile)

		renderer_text = Gtk.CellRendererText()
		column_text = Gtk.TreeViewColumn("Fichier", renderer_text, text=0)
		self.treeview_file.append_column(column_text)

		renderer_text_action = Gtk.CellRendererText()
		column_text = Gtk.TreeViewColumn("Action", renderer_text_action, text=1)
		self.treeview_file.append_column(column_text)

		renderer_toggle = Gtk.CellRendererToggle()
		renderer_toggle.connect("toggled", self.on_cell_toggled_file)
		tree_view_column_toggle = Gtk.TreeViewColumn("Modifier", renderer_toggle, active=2)
		self.treeview_file.append_column(tree_view_column_toggle)

		self.scrolled_win_select_file.add(self.treeview_file)

		self.button_compare = Gtk.Button.new_with_label('Comparer')
		self.button_compare.connect('clicked', self.compare)
		self.button_execute = Gtk.Button.new_with_label('Executer')
		self.button_execute.connect('clicked', self.execute_compare)
		self.button_execute.set_sensitive(False)
		self.grid.attach(self.button_compare, 0, 10, 1, 1)
		self.grid.attach(self.button_execute, 1, 10, 1, 1)

		self.add(self.grid)

		# Menubar
		show_saved_action = Gio.SimpleAction.new('show_saved')
		show_saved_action.connect('activate', self.show_saved)
		self.add_action(show_saved_action)

		settings_action = Gio.SimpleAction.new('settings')
		settings_action.connect('activate', self.settings)
		self.add_action(settings_action)

		compare_action = Gio.SimpleAction.new('compare')
		compare_action.connect('activate', self.compare)
		self.add_action(compare_action)

		start_watching_action = Gio.SimpleAction.new('start_watching')
		start_watching_action.connect('activate', lambda *arg: self.switch_start.set_active(True))
		self.add_action(start_watching_action)

		stop_watching_action = Gio.SimpleAction.new('stop_watching')
		stop_watching_action.connect('activate', lambda *arg: self.switch_start.set_active(False))
		self.add_action(stop_watching_action)

		watch_now_action = Gio.SimpleAction.new('watch_now')
		watch_now_action.connect('activate', self.scan_now)
		self.add_action(watch_now_action)

		about_action = Gio.SimpleAction.new('about')
		about_action.connect('activate', self.about)
		self.add_action(about_action)

		# Initialize config
		for watched_dir in self.safer.config['delicate_dirs']:
			self.watched_list.append_text(watched_dir)

	def on_switch_activate(self, switch, active):
		"""This start or stop perpetual scan."""
		if switch.get_active():
			self.start_scan()
		else:
			self.stop_watching()

	def on_button_toggled(self, button, name):
		if button.get_active():
			self.state = name

	def on_button_select_toggled(self, button, name):
		if button.get_active():
			state = "on"
		else:
			state = "off"
		print("Button", name, "was turned", state)

	def on_cell_toggled_file(self, widget, path):
		print('on cell toggled file')
		print(path)
		new_val = not self.listfile[path][2]
		self.listfile[path][2] = new_val
		print(self.listfile[path])  # model row
		print(self.listfile[path][2])  # bool: is selected or not ?
		print(self.safer.safe_dirs)

	#################### SCAN ####################

	def scan_now(self, *args):  # start the thread
		"""Make thread, that scan and copy files, if no one is already started."""
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
		"""
		elif self.state == 'compare':
			comparison = self.safer.compare(loop=self.loop)
			self.compare(comparison)
		"""

		end = time()
		self.scan_time = round(end - begin, 2)
		self.spinner.stop()
		self.text.set_text('Scanné en ' + str(self.scan_time) + ' s')

	def compare(self, button):
		# Call by the button
		# TODO : reset self.listfile
		comparison = self.safer.compare(loop=self.loop)
		print("compare")
		print(comparison)
		for filename in comparison['to_copy']:
			self.listfile.append([filename, 'Copier', True])

		for filename in comparison['to_update']:
			self.listfile.append([filename, 'MAJ', True])

		for filename in comparison['to_del']:
			self.listfile.append([filename, 'Supprimer', True])

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
			print(self.listfile[path][1])
			print(self.listfile[path][0])
			if self.listfile[path][2]:  # is ok ?
				if self.listfile[path][1] == 'Copier':
					results['to_copy'].append(self.listfile[path][0])
				if self.listfile[path][1] == 'MAJ':
					results['to_update'].append(self.listfile[path][0])
				if self.listfile[path][1] == 'Supprimer':
					results['to_del'].append(self.listfile[path][0])

		results['dirs_to_make'] = self.comparison['dirs_to_make']
		results['dirs_to_del'] = self.comparison['dirs_to_del']
		print(results)

		self.safer.execute(results, path_delicate)
		# spinner and timer
		self.button_compare.set_sensitive(True)
		self.button_execute.set_sensitive(False)

	def start_scan(self):  # perpetual scan
		"""Run `scan_now`, start a timer thread to itself for perpetual scan."""
		self.text.set_text('Surveillance active')
		self.scan_now()
		self.timer = threading.Timer(self.safer.config['timedelta']*10, self.start_scan)
		self.timer.start()

	def stop_watching(self):
		"""Cancel timer thread."""
		if self.timer.is_alive():
			self.timer.cancel()
			self.timer.join()
		self.text.set_text('En attente...')

	def copy_dir(self, *args):
		self.safer.copy()

	def show_saved(self, *args):
		"""Open in nautilus or file explorer, in the safe directory."""
		if SYSTEM == 'Linux':
			Popen(['xdg-open', self.safer.config['safe_dir']])
		elif SYSTEM == 'Windows':
			startfile(self.safer.config['safe_dir'])

	def settings(self, *args):
		"""Open the setting dialog."""
		dialog_settings = Settings_dial(self)
		dialog_settings.run()

	def dialog_info(self, *args):
		msg = 'Scanné en: ' + str(self.scan_time) + ' s.'
		msg_dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, msg)
		msg_dialog.run()
		msg_dialog.destroy()

	def add_watched_dir(self, button):
		# TODO: add in radio button
		"""Add a dirctory to scan."""
		tree_iter = self.watched_list.get_active_iter()
		if tree_iter is None:
			new_dir = self.watched_list.get_child().get_text()
			if new_dir != '' and new_dir not in self.safer.config['delicate_dirs'] and path.exists(new_dir):
				self.watched_list.append_text(new_dir)
				self.safer.add_delicate_dir(new_dir)
				self.
				self.text.set_text('Dossier ajouté')

	def del_watched_dir(self, button):
		"""Remove a directory to scan."""
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

	def about(self, action, parameter):
		"""Open the about dialog."""
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

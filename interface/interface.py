#!/usr/bin/python3

import os

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GdkPixbuf


from .auto_save import AutoSavingGrid
from .synchronisation import SynchronisationGrid
from .dialogs.settings import SettingsDialog
from safer.safe import Safer

class MyWindow(Gtk.ApplicationWindow):
	'''Application.'''
	def __init__(self, app):
		Gtk.Window.__init__(self, title='SafeMyWork 1.0', application=app)
		self.smw_exe_path = os.getcwd()
		# Varaibles
		self.safer = Safer()
		# Properties
		self.set_position(Gtk.WindowPosition.CENTER)
		self.set_border_width(5)
		self.set_icon_from_file('icon.png')

		# Header Bar
		hb = Gtk.HeaderBar()
		hb.set_show_close_button(True)
		hb.props.title = 'SafeMyWork!'
		hb.props.subtitle = 'Save and sync your files'
		self.set_titlebar(hb)

		button = Gtk.Button()
		icon = Gio.ThemedIcon(name='preferences-system')
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		button.connect('clicked', self.settings)
		button.add(image)
		hb.pack_end(button)

		button = Gtk.Button()
		icon = Gio.ThemedIcon(name='help-about')
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		button.connect('clicked', self.about)
		button.add(image)
		hb.pack_end(button)

		# Main box
		main_box = Gtk.VBox(spacing=6)
		self.add(main_box)

		# Header box
		header_box = Gtk.Box(spacing=6)
		self.info_label = Gtk.Label('Welcome!')
		header_box.pack_start(self.info_label, True, True, 0)
		main_box.pack_start(header_box, False, False, 0)

		# Notebook
		self.notebook = Gtk.Notebook()
		main_box.pack_start(self.notebook, True, True, 0)

		# Auto-saving page
		self.page_auto_save = AutoSavingGrid(self, self.safer)
		self.notebook.append_page(self.page_auto_save, Gtk.Label('Auto-saving'))

		# Synchronisation page
		page_synchronisation = SynchronisationGrid(self, self.safer)
		self.notebook.append_page(page_synchronisation, Gtk.Label('Sync'))

	def settings(self, _):
		'''Open the setting dialog.'''
		dialog_settings = SettingsDialog(self)
		dialog_settings.run()
		self.page_auto_save.spinbutton.set_value(self.safer.config['timedelta'])

	def about(self, _):
		'''Open the about dialog.'''
		about_dialog = Gtk.AboutDialog(transient_for=self)
		about_dialog.set_program_name('SafeMyWork')
		about_dialog.set_version('0.6.2')
		about_dialog.set_website('https://github.com/Thykof/SafeMyWork')
		about_dialog.set_website_label('Github')
		about_dialog.set_authors(['Nathan Seva'])
		about_dialog.set_license('SafeMyWork is under GNU GPL(v3) license. \n\n https://github.com/Thykof/SafeMyWork/blob/master/LICENSE')
		pixbuf = GdkPixbuf.Pixbuf.new_from_file(os.path.join(self.smw_exe_path, 'logo_smw.png'))
		about_dialog.set_logo(pixbuf)

		about_dialog.run()
		about_dialog.destroy()

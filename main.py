#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
import sys


from interface.interface import MyWindow


class MyApplication(Gtk.Application):
	def __init__(self):
		Gtk.Application.__init__(self)

	def do_activate(self):
		self.win = MyWindow(self)
		self.win.connect('delete-event', self.quit_callback)
		self.win.show_all()

	def do_startup(self):
		Gtk.Application.do_startup(self)

		quit_action = Gio.SimpleAction.new('quit', None)
		quit_action.connect('activate', self.quit_callback)
		self.add_action(quit_action)

		builder = Gtk.Builder()
		builder.add_from_file('interface/menubar.ui')

		self.set_menubar(builder.get_object('menubar'))

	def quit_callback(self, action, parameter):
		self.win.text.set_text('Fermeture')
		self.win.safer.save_config()
		self.win.switch_start.set_active(False)
		sys.exit()

if __name__ == '__main__':
	app = MyApplication()
	app.run()

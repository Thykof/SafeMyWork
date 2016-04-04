# -*- coding: utf-8 -*-
#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
import sys

from watcher import conf
from interface.interface import MyWindow

myfile = open('stderr.log', 'a')
sys.stderr = myfile

class MyApplication(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        self.win = MyWindow(self, conf.get_config())
        self.win.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)

        quit_action = Gio.SimpleAction.new('quit', None)
        quit_action.connect('activate', self.quit_callback)
        self.add_action(quit_action)

        builder = Gtk.Builder()
        try:
            builder.add_from_file('interface/menubar.ui')
        except:
            from interface.menubar_ui import UI_INFO
            builder.add_from_string(UI_INFO)

        self.set_menubar(builder.get_object('menubar'))

    def quit_callback(self, action, parameter):
        self.win.grid.text.set_text('Fermeture')
        conf.save_config(self.win.config)
        self.win.grid.switch_start.set_active(False)
        self.win.stop_watching()
        sys.exit()

if __name__ == '__main__':
    app = MyApplication()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)

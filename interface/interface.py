# -*- coding: utf-8 -*-
#!/usr/bin/python3

from gi.repository import Gtk
from threading import Timer

from .menu import create_menus
from .tools import about

class Interface(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title='SafeMyWork 1.0')
        self.set_default_size(800, 400)
        self.connect('destroy', Gtk.main_quit)

        grid = Gtk.Grid()
        self.add(grid)

        menus = create_menus(self)
        grid.add(menus[0])
        grid.attach(menus[1], 0, 0, 1, 1)

    def set_watcher(self, watcher):
        self.watcher = watcher

    def run(self):
        self.show_all()
        Gtk.main()

    def start_watching(self, *args):
        self.watcher.watch()
        self.thread = Timer(self.watcher.config['time_delta'], self.start_watching)
        self.thread.start()

    def stop_watching(self, *args):
        self.thread.cancel()

    def add_dir(self, *args):
        pass

    def show_saved(self, *args):
        pass

    def quit(self, *args):
        Gtk.main_quit()

    def settings(self, *args):
        pass

    def check_now(self, *args):
        self.watcher.watch()

    def about(self, *args):
        about()

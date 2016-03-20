# -*- coding: utf-8 -*-
#!/usr/bin/python3

from gi.repository import Gtk
from threading import Timer

from .menubar import create_menus
from .tools import about, initialize_interface
import watcher
from watcher.watcher import Watcher

class Interface(Gtk.Window):
    def __init__(self, config):
        Gtk.Window.__init__(self, title='SafeMyWork 1.0')
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect('delete-event', self.quit_app)

        self.grid = initialize_interface(self)
        self.grid.add(create_menus(self))

        self.add(self.grid)

        self.thread = None
        self.config = config
        self.watcher = Watcher(config)

    def run(self):
        self.show_all()
        Gtk.main()

    def quit_app(self, *args):
        Gtk.main_quit()
        self.save_config(self.config)
        self.stop_watching()

    def save_config(self, config=watcher.data.DEFAULT_CONFIG):
        watcher.mod.tell('Save config')
        watcher.conf.save_config(config)

    def on_switch_activated(self, switch, *args):
        if switch.get_active():
            self.start_watching()
        else:
            self.stop_watching()

    def start_watching(self, *args):
        self.watcher.watch()
        self.thread = Timer(self.watcher.config['time_delta'], self.start_watching)
        self.thread.start()

    def stop_watching(self, *args):
        if self.thread is not None:
            self.thread.cancel()

    def show_saved(self, *args):
        pass

    def settings(self, *args):
        pass

    def check_now(self, *args):
        self.watcher.watch()

    def about(self, *args):
        about()

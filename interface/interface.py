# -*- coding: utf-8 -*-
#!/usr/bin/python3

from gi.repository import Gtk
from threading import Timer

from .menubar import create_menus
from .tools import about

class Interface(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title='SafeMyWork 1.0')
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect('delete-event', self.quit_app)

        self.grid = Gtk.Grid(column_spacing=20, row_spacing=20)
        self.add(self.grid)

        self.create_buttons()
        self.grid.add(create_menus(self))

        self.thread = None

    def create_buttons(self):
        button_show_saved = Gtk.Button.new_with_label('Fichiers sauvés')
        button_show_saved.connect('clicked', self.show_saved)
        button_check_now = Gtk.Button.new_with_label('Scanner maintenant')
        button_check_now.connect('clicked', self.check_now)
        label_watch = Gtk.Label('Scan :')
        switch_start = Gtk.Switch()
        switch_start.connect('notify::active', self.on_switch_activated)
        switch_start.set_active(False)

        self.grid.attach(button_show_saved, 0, 0, 1, 1)
        self.grid.attach(button_check_now, 1, 0 , 1, 1)
        self.grid.attach(label_watch, 0, 1 , 1, 1)
        self.grid.attach(switch_start, 1, 1 , 1 , 1)
        switch_start.do_grab_focus(switch_start)

    def on_switch_activated(self, switch, *args):
        if switch.get_active():
            self.start_watching()
        else:
            self.stop_watching()

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
        if self.thread is not None:
            self.thread.cancel()

    def show_saved(self, *args):
        pass

    def quit_app(self, *args):
        Gtk.main_quit()
        self.stop_watching()

    def settings(self, *args):
        pass

    def check_now(self, *args):
        self.watcher.watch()

    def about(self, *args):
        about()

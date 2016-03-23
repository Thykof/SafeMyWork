# -*- coding: utf-8 -*-
#!/usr/bin/python3

from gi.repository import Gtk
import threading
from os import path

from .menubar import create_menus
from .tools import about, initialize_interface
from .dialog import show_watched_dialog, del_dir_dialog
import watcher
from watcher.watcher import Watcher

class Interface(Gtk.Window):
    def __init__(self, config):
        Gtk.Window.__init__(self, title='SafeMyWork 1.0')
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(5)
        self.connect('delete-event', self.quit_app)

        initialize_interface(self)
        self.switch_start.do_grab_focus(self.switch_start)
        self.grid.add(create_menus(self))
        self.add(self.grid)

        self.thread = None
        self.config = config
        self.watcher = Watcher(config)

        self.initialize_config()

    def initialize_config(self):
        for watched_dir in self.config['watched_dirs']:
            self.watched_list.append_text(watched_dir)
        for ext in self.config['exclude_ext']:
            self.ext_list.append_text(ext)

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

    def start_watching(self, *args):
        if not self.switch_start.get_active():
            self.switch_start.set_active(True)

    def watching(self, *args):
        self.text.set_text('Scan en cours')
        self.spinner.start()
        self.watcher.watch()
        self.spinner.stop()
        self.thread = threading.Timer(self.watcher.config['time_delta'], self.watching)
        self.thread.start()

    def stop_watching(self, action=None):
        if self.switch_start.get_active():
            self.switch_start.set_active(False)

    def cancel_watching(self):
        self.text.set_text('Scan annulé')
        if self.thread is not None:
            self.thread.cancel()

    def show_saved(self, *args):
        pass

    def show_watched(self, *args):
        show_watched_dialog(self)

    def settings(self, *args):
        self.show_watched()

    def watch_now(self, *args):
        self.spinner.start()
        self.watcher.watch()
        self.spinner.stop()

    def add_watched_dir(self, button):
        tree_iter = self.watched_list.get_active_iter()
        if tree_iter is None:
            new_dir = self.watched_list.get_child().get_text()
            if new_dir != '' and new_dir not in self.config['watched_dirs'] and path.exists(new_dir):
                print("add dir: " + new_dir)
                self.watched_list.append_text(new_dir)
                self.config['watched_dirs'].append(new_dir)
                self.text.set_text('Dossier ajouté')

    def del_watched_dir(self, button):
        tree_iter = self.watched_list.get_active_iter()
        if tree_iter is not None:
            model = self.watched_list.get_model()
            directory = model[tree_iter][0]
            must_del, dialog = del_dir_dialog(self, directory)
            dialog.destroy()
            if must_del:
                print("delete dir :" + directory)
                self.config['watched_dirs'].remove(directory)
                self.watched_list.remove(int(self.watched_list.get_active()))
                self.text.set_text('Dossier supprimé')

    def about(self, *args):
        about()

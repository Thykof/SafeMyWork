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
from .dialog import edit_settings_dialog, del_dir_dialog
from watcher.watcher import Watcher
import watcher

SYSTEM = system()
if SYSTEM == 'Linux':
    from subprocess import Popen
elif SYSTEM == 'Windows':
    from os import startfile
else:
    watcher.mod.tell('Import Error')

class Interface(Gtk.Window):
    def __init__(self, config):
        Gtk.Window.__init__(self, title='SafeMyWork 1.0')
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(5)
        self.connect('delete-event', self.quit_app)

        self.grid = MainGrid(self)
        self.add(self.grid)
        self.grid.switch_start.do_grab_focus(self.grid.switch_start)

        menubar = create_menus(self)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(menubar, False, False, 0)
        self.grid.add(box)

        self.config = config
        self.watcher = Watcher(self.config)
        self.timer = None
        self.thread = None

        self.initialize_config()

    def initialize_config(self):
        for watched_dir in self.config['watched_dirs']:
            self.grid.watched_list.append_text(watched_dir)

    def run(self):
        self.show_all()
        Gtk.main()

    def quit_app(self, *args):
        Gtk.main_quit()
        self.save_config(self.config)
        self.stop_watching()
        self.abort_watch()

    def save_config(self, config=watcher.data.DEFAULT_CONFIG):
        watcher.mod.tell('Save config')
        watcher.conf.save_config(config)

    def watch(self, loop):
        """Launch watch"""
        self.grid.spinner.start()
        self.watcher.watch()
        self.grid.spinner.stop()
        if loop:
            self.timer = threading.Timer(self.config['time_delta'], self.start_watching, args=(loop,))
            self.timer.start()

    def start_watching(self, loop):
        """Start watching : watch + timer"""
        can = True
        for thread in threading.enumerate():
            print(thread)
            if thread.name == 'watcher_loop' or thread.name == 'watcher_alone':
                if thread.is_alive():
                    print('no!')
                    can = False
        if can:
            print('yes!')
            self.thread = threading.Thread(target=self.watch, name='watcher_loop', args=(loop,))
            self.thread.start()

    def stop_watching(self):
        """Cancel timer"""
        if self.timer is not None:
            self.timer.cancel()

    def abort_watch(self):
        """Abort current watch"""
        self.watcher.stop = True

    def show_saved(self, *args):
        if SYSTEM == 'Linux':
            Popen(['xdg-open', self.config['archive_dir']])
        elif SYSTEM == 'Windows':
            startfile(self.config['archive_dir'])

    def settings(self, *args):
        edit_settings_dialog(self)

    def add_watched_dir(self, button):
        tree_iter = self.grid.watched_list.get_active_iter()
        if tree_iter is None:
            new_dir = self.grid.watched_list.get_child().get_text()
            if new_dir != '' and new_dir not in self.config['watched_dirs'] and path.exists(new_dir):
                self.grid.watched_list.append_text(new_dir)
                self.config['watched_dirs'].append(new_dir)
                self.grid.text.set_text('Dossier ajouté')

    def del_watched_dir(self, button):
        tree_iter = self.grid.watched_list.get_active_iter()
        if tree_iter is not None:
            model = self.grid.watched_list.get_model()
            directory = model[tree_iter][0]
            must_del, dialog = del_dir_dialog(self, directory)
            dialog.destroy()
            if must_del:
                self.config['watched_dirs'].remove(directory)
                self.grid.watched_list.remove(int(self.grid.watched_list.get_active()))
                self.grid.text.set_text('Dossier supprimé')

    def about(self, *args):
        about()

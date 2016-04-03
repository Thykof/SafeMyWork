# -*- coding: utf-8 -*-
#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def about():
    dialog = Gtk.AboutDialog()
    dialog.set_program_name('SafeMyWork')
    dialog.set_version('1.0')
    dialog.set_website('https://github.com/Thykof/SafeMyWork')
    dialog.set_authors(['Nathan Seva'])
    dialog.set_comments('Utilitaire SafeMyWork')
    dialog.set_license('SafeMyWork est sous la license GNU GPL(v3). \n\n https://github.com/Thykof/SafeMyWork/blob/master/LICENSE')

    dialog.run()
    dialog.destroy()

class MainGrid(Gtk.Grid):
    """docstring for Grid"""
    def __init__(self, parent):
        super(MainGrid, self).__init__()
        self.parent = parent
        self.set_column_spacing(5)
        self.set_row_spacing(5)
        self.initialize_grid()

    def initialize_grid(self):
        self.text = Gtk.Label('En attente...')
        # Toolbar:
        button_show_saved = Gtk.Button.new_with_label('Fichiers sauvés')
        button_show_saved.connect('clicked', self.parent.show_saved)
        button_check_now = Gtk.Button.new_with_label('Scanner maintenant')
        button_check_now.connect('clicked', self.on_check_now_clicked)
        # Watching:
        self.switch_start = Gtk.Switch()
        self.switch_start.connect('notify::active', self.on_switch_activated)
        self.switch_start.set_active(False)
        # Watched dirs:
        self.watched_list = Gtk.ComboBoxText.new_with_entry()
        button_add_watched = Gtk.Button.new_with_label('Ajouter')
        button_add_watched.connect('clicked', self.parent.add_watched_dir)
        button_del_watched = Gtk.Button.new_with_label('Supprimer')
        button_del_watched.connect('clicked', self.parent.del_watched_dir)
        self.spinner = Gtk.Spinner()

        # pack:
        hbox = Gtk.Box(spacing=6)
        hbox.pack_start(self.text, True, True, 0)
        hbox.pack_start(self.switch_start, True, True, 0)
        hbox.pack_start(self.spinner, True, True, 0)
        self.attach(hbox, 0, 1, 2, 1)

        self.attach(button_show_saved, 0, 0, 1, 1)
        self.attach(button_check_now, 1, 0 , 1, 1)
        self.attach(self.watched_list, 0, 2, 2, 1)
        self.attach(button_add_watched, 0, 3, 1, 1)
        self.attach(button_del_watched, 1, 3, 1, 1)

    def on_switch_activated(self, switch, active):
        if switch.get_active():
            self.parent.start_watching(True)
        else:
            self.parent.stop_watching()

    def on_check_now_clicked(self, button):
        self.parent.start_watching(False)

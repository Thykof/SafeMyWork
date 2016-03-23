# -*- coding: utf-8 -*-
#!/usr/bin/python3

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

def initialize_interface(self):
    self.grid = Gtk.Grid(column_spacing=5, row_spacing=5)
    self.text = Gtk.Label('En attente...')
    # Toolbar:
    button_show_saved = Gtk.Button.new_with_label('Fichiers sauvés')
    button_show_saved.connect('clicked', self.show_saved)
    button_check_now = Gtk.Button.new_with_label('Scanner maintenant')
    button_check_now.connect('clicked', self.watch_now)
    # Watching:
    self.switch_start = Gtk.Switch()
    self.switch_start.connect('notify::active', on_switch_activated, self)
    self.switch_start.set_active(False)
    # Watched dirs:
    self.watched_list = Gtk.ComboBoxText.new_with_entry()
    self.watched_list.connect('changed', on_changed_watched)
    button_add_watched = Gtk.Button.new_with_label('Ajouter')
    button_add_watched.connect('clicked', self.add_watched_dir)
    button_del_watched = Gtk.Button.new_with_label('Supprimer')
    button_del_watched.connect('clicked', self.del_watched_dir)
    self.spinner = Gtk.Spinner()

    # pack:
    hbox = Gtk.Box(spacing=6)
    hbox.pack_start(self.text, True, True, 0)
    hbox.pack_start(self.switch_start, True, True, 0)
    hbox.pack_start(self.spinner, True, True, 0)
    self.grid.attach(hbox, 0, 1, 2, 1)

    self.grid.attach(button_show_saved, 0, 0, 1, 1)
    self.grid.attach(button_check_now, 1, 0 , 1, 1)
    self.grid.attach(self.watched_list, 0, 2, 2, 1)
    self.grid.attach(button_add_watched, 0, 3, 1, 1)
    self.grid.attach(button_del_watched, 1, 3, 1, 1)

def on_changed_ext(ext_list):
    tree_iter = ext_list.get_active_iter()
    if tree_iter != None:
        model = ext_list.get_model()
        print(model)
    else:
        entry = ext_list.get_child()
        print("Entered: " + entry.get_text())

def on_changed_watched(watched_list):
    pass

def on_switch_activated(switch, active, self):
    if switch.get_active():
        self.watching()
    else:
        self.cancel_watching()

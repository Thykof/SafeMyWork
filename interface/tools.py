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
    grid = Gtk.Grid(column_spacing=20, row_spacing=20)
    button_show_saved = Gtk.Button.new_with_label('Fichiers sauvés')
    button_show_saved.connect('clicked', self.show_saved)
    button_check_now = Gtk.Button.new_with_label('Scanner maintenant')
    button_check_now.connect('clicked', self.check_now)
    label_watch = Gtk.Label('Scan :')
    switch_start = Gtk.Switch()
    switch_start.connect('notify::active', self.on_switch_activated)
    switch_start.set_active(False)

    grid.attach(button_show_saved, 0, 0, 1, 1)
    grid.attach(button_check_now, 1, 0 , 1, 1)
    grid.attach(label_watch, 0, 1 , 1, 1)
    grid.attach(switch_start, 1, 1 , 1 , 1)
    switch_start.do_grab_focus(switch_start)

    return grid

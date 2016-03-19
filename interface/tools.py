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

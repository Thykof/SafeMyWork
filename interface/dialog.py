# -*- coding: utf-8 -*-
#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def edit_settings_dialog(self):
    dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
        Gtk.ButtonsType.OK, "Dossiers surveillés")
    dialog.format_secondary_text(str(self.config))
    dialog.run()
    dialog.destroy()

def del_dir_dialog(self, directory):
    dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.YES_NO, "Ne plus surveiller " + directory + " ?")
    response = dialog.run()
    return response == Gtk.ResponseType.YES, dialog

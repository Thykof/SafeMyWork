# -*- coding: utf-8 -*-
#!/usr/bin/python3

from gi.repository import Gtk

def create_menus(self):
    action_group = Gtk.ActionGroup(name='menu')

    action_FileMenu = Gtk.Action(name="FileMenu", label="Fichier")
    action_group.add_action(action_FileMenu)

    action_Settings = Gtk.Action(name='Settings', label='Préférences')
    action_Settings.connect('activate', self.settings)
    action_group.add_action(action_Settings)

    action_Quit = Gtk.Action(name='Quit', label='Quitter')
    action_Quit.connect('activate', self.quit_app)
    action_group.add_action(action_Quit)

    action_ActionMenu = Gtk.Action(name="ActionMenu", label="Action")
    action_group.add_action(action_ActionMenu)

    action_Start = Gtk.Action(name='Start', label='Démmarer le scan')
    action_Start.connect('activate', self.start_watching)
    action_group.add_action(action_Start)

    action_Stop = Gtk.Action(name='Stop', label='Arrêter le scan')
    action_Stop.connect('activate', self.stop_watching)
    action_group.add_action(action_Stop)

    action_CheckNow = Gtk.Action(name='CheckNow', label='Scanner maintenant')
    action_CheckNow.connect('activate', self.watch_now)
    action_group.add_action(action_CheckNow)

    action_OpenSaved = Gtk.Action(name='OpenSaved', label='Afficher les fichiers sauvegardés')
    action_OpenSaved.connect('activate', self.show_saved)
    action_group.add_action(action_OpenSaved)

    action_HelpMenu = Gtk.Action(name="HelpMenu", label="Aide")
    action_group.add_action(action_HelpMenu)

    action_About = Gtk.Action(name='About', label='À propos')
    action_About.connect('activate', self.about)
    action_group.add_action(action_About)

    uimanager = Gtk.UIManager()
    uimanager.add_ui_from_file('interface/menubar.ui')
    uimanager.insert_action_group(action_group)

    return uimanager.get_widget("/MenuBar")

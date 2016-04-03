# -*- coding: utf-8 -*-
#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

UI_INFO = """
<ui>
  <menubar name="MenuBar">
    <menu action="FileMenu">
      <menuitem action="OpenSaved" />
      <menuitem action="Settings" />
      <menuitem action="Quit" />
    </menu>
    <menu action="ActionMenu">
      <menuitem action="Start" />
      <menuitem action="Stop" />
      <menuitem action="CheckNow" />
    </menu>
    <menu action="HelpMenu">
      <menuitem action="About" />
    </menu>
  </menubar>
</ui>
"""

def create_menus(parent):
    action_group = Gtk.ActionGroup(name='menu')

    action_FileMenu = Gtk.Action(name="FileMenu", label="Fichier")
    action_group.add_action(action_FileMenu)

    action_Settings = Gtk.Action(name='Settings', label='Préférences')
    action_Settings.connect('activate', parent.settings)
    action_group.add_action(action_Settings)

    action_Quit = Gtk.Action(name='Quit', label='Quitter')
    action_Quit.connect('activate', parent.quit_app)
    action_group.add_action(action_Quit)

    action_ActionMenu = Gtk.Action(name="ActionMenu", label="Action")
    action_group.add_action(action_ActionMenu)

    action_Start = Gtk.Action(name='Start', label='Démmarer le scan')
    action_Start.connect('activate', lambda arg: start_watching(parent))
    action_group.add_action(action_Start)

    action_Stop = Gtk.Action(name='Stop', label='Arrêter le scan')
    action_Stop.connect('activate', lambda arg: stop_watching(parent))
    action_group.add_action(action_Stop)

    action_CheckNow = Gtk.Action(name='CheckNow', label='Scanner maintenant')
    action_CheckNow.connect('activate', lambda arg: parent.start_watching(False))
    action_group.add_action(action_CheckNow)

    action_OpenSaved = Gtk.Action(name='OpenSaved', label='Afficher les fichiers sauvegardés')
    action_OpenSaved.connect('activate', parent.show_saved)
    action_group.add_action(action_OpenSaved)

    action_HelpMenu = Gtk.Action(name="HelpMenu", label="Aide")
    action_group.add_action(action_HelpMenu)

    action_About = Gtk.Action(name='About', label='À propos')
    action_About.connect('activate', parent.about)
    action_group.add_action(action_About)

    uimanager = Gtk.UIManager()
    uimanager.add_ui_from_string(UI_INFO)
    uimanager.insert_action_group(action_group)
    menubar = uimanager.get_widget("/MenuBar")

    return menubar

def start_watching(parent):
    if not parent.grid.switch_start.get_active():
        parent.grid.switch_start.set_active(True)

def stop_watching(parent):
    if parent.grid.switch_start.get_active():
        parent.grid.switch_start.set_active(False)

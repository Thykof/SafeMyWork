# -*- coding: utf-8 -*-
#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio

from .tools import about

def create_menus(parent):
    show_saved_action = Gio.SimpleAction.new('show_saved')
    show_saved_action.connect('activate', parent.show_saved)
    parent.add_action(show_saved_action)

    settings_action = Gio.SimpleAction.new('settings')
    settings_action.connect('activate', parent.settings)
    parent.add_action(settings_action)

    start_watching_action = Gio.SimpleAction.new('start_watching')
    start_watching_action.connect('activate', start_watching, parent)
    parent.add_action(start_watching_action)

    stop_watching_action = Gio.SimpleAction.new('stop_watching')
    stop_watching_action.connect('activate', stop_watching, parent)
    parent.add_action(stop_watching_action)

    watch_now_action = Gio.SimpleAction.new('watch_now')
    watch_now_action.connect('activate', wtach_now, parent)
    parent.add_action(watch_now_action)

    about_action = Gio.SimpleAction.new('about')
    about_action.connect('activate', show_about, parent)
    parent.add_action(about_action)

def start_watching(action, parameter, parent):
    if not parent.grid.switch_start.get_active():
        parent.grid.switch_start.set_active(True)

def stop_watching(action, parameter, parent):
    if parent.grid.switch_start.get_active():
        parent.grid.switch_start.set_active(False)

def show_about(action, parameter, parent):
    about(parent)

def wtach_now(action, parameter, parent):
    parent.start_watching(False)

#!/usr/bin/python3

import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib

class Thread(threading.Thread):
	def __init__(self, target, callback, name=None):
		super().__init__()
		self.name = name
		self.daemon = True
		self.target = target
		self.callback = callback

	def run(self):
		self.target()
		GLib.idle_add(self.callback)

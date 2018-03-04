#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import datetime

class ConflictDialog(Gtk.Dialog):
	def __init__(self, parent, comparison, mysync, max_conflicts):
		Gtk.Dialog.__init__(self, "Conflits", parent, 0,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			Gtk.STOCK_OK, Gtk.ResponseType.OK))

		# Varaibles
		self.parent = parent
		self.mysync = mysync
		self.max_conflicts = max_conflicts
		self.results = None  # orders
		self.comparison = comparison
		self.conflicts = comparison['conflicts']
		self.paths = comparison['paths']

		# Properties
		self.set_border_width(10)
		self.set_modal(True)
		self.set_default_size(800, 400)

		# Content
		self.box = self.get_content_area()
		self.initialise_box()

		self.show_all()

	def on_button_toggled(self, button, path_type, num):
		print('toggle')
		if button.get_active():
			print('yes active')
			self.mysync.change_dst(path_type, num)

	def initialise_box(self):
		self.box.set_spacing(6)
		self.box.pack_start(Gtk.Label('List of conflicts :'), False, False, 5)
		box_conflicts = Gtk.VBox()
		scrolled = Gtk.ScrolledWindow()
		show_confilcts = self.conflicts
		if len(self.conflicts) > self.max_conflicts and self.parent.safer.config['advanced'] == False:
			self.box.pack_start(Gtk.Label("There is more than {} conflicts, \
			they are not all show here. You should sync subfolders before.".format(self.max_conflicts)), False, False, 5)
			show_confilcts = self.conflicts[0:self.max_conflicts]
		for i, fileinfo in enumerate(show_confilcts):  # self.conflicts = comparison['conflicts']
			# fileinfo [0]: filename
			# fileinfo [1]: tuple size
			# fileinfo [2]: tuple date
			box = Gtk.VBox()
			box.pack_start(Gtk.Label(fileinfo[0]), False, False, 5)

			date_local = datetime.datetime.fromtimestamp(fileinfo[2][0]).strftime('%c')
			local_text = 'In ' + self.paths[0] + ' , last modification : '
			local_text += date_local + ' , size : ' + str(int(fileinfo[1][0])/1000) + ' Ko'
			radio_local = Gtk.RadioButton.new_with_label_from_widget(None, local_text)
			radio_local.connect("toggled", self.on_button_toggled, "local", i)

			date_ext = datetime.datetime.fromtimestamp(fileinfo[2][1]).strftime('%c')
			ext_text = 'In ' + self.paths[1] + ' , last modification : '
			ext_text += date_ext + ' , size : ' + str(int(fileinfo[1][1])/1000) + ' Ko'
			radio_ext = Gtk.RadioButton.new_with_label_from_widget(radio_local, ext_text)
			radio_ext.connect("toggled", self.on_button_toggled, "ext", i)

			if fileinfo[2][0] > fileinfo[2][1]:  # local is more recent
				box.pack_start(radio_local, False, False, 1)
				box.pack_start(radio_ext, False, False, 1)
				radio_local.set_active(True)
				self.mysync.change_dst('local', i)
			else:
				box.pack_start(radio_ext, False, False, 1)
				box.pack_start(radio_local, False, False, 1)
				radio_ext.set_active(True)
				self.mysync.change_dst('ext', i)

			box_conflicts.pack_start(box, False, False, 5)

			# end for

		if len(show_confilcts) != len(self.conflicts):
			box_default = Gtk.Box()
			box_default.pack_start(Gtk.Label('Default conflict resolution\nfor every not shown conflicts?'), False, False, 0)
			self.switch = Gtk.Switch()
			box_default.pack_start(self.switch, False, False, 5)
			box_conflicts.pack_start(box_default, False, False, 10)

		scrolled.add(box_conflicts)
		self.box.pack_start(scrolled, True, True, 2)

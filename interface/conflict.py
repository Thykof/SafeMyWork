#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import datetime

class ConflictDialog(Gtk.Dialog):
	def __init__(self, parent, comparison):
		Gtk.Dialog.__init__(self, "Conflits", parent, 0,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			Gtk.STOCK_OK, Gtk.ResponseType.OK))

		# Varaibles
		self.parent = parent
		self.results = None  # orders
		self.comparison = comparison
		self.conflicts = comparison['conflicts']
		self.paths = comparison['working_paths']

		# Properties
		self.set_border_width(10)
		self.set_modal(True)

		# Content
		self.box = self.get_content_area()
		self.initialise_box()

		self.show_all()

	def add_in_local(self, filename):
		self.comparison['copy_file_in_local'].append(filename)

	def remove_in_local(self, filename):
		self.comparison['copy_file_in_local'].remove(filename)

	def add_in_ext(self, filename):
		self.comparison['copy_file_ext'].append(filename)

	def remove_in_ext(self, filename):
		self.comparison['copy_file_ext'].remove(filename)

	def on_button_toggled(self, button, path_type, num):
		if button.get_active():
			if path_type == 'ext':
				if self.conflicts[num][0] not in self.comparison['copy_file_in_local']:
					self.add_in_local(self.conflicts[num][0])
				if self.conflicts[num][0] in self.comparison['copy_file_ext']:
					self.remove_in_ext(self.conflicts[num][0])
			else:  # path_type == 'local'
				if self.conflicts[num][0] not in self.comparison['copy_file_ext']:
					self.add_in_ext(self.conflicts[num][0])
				if self.conflicts[num][0] in self.comparison['copy_file_in_local']:
					self.remove_in_local(self.conflicts[num][0])

	def initialise_box(self):
		self.box.set_spacing(6)
		self.box.pack_start(Gtk.Label('Liste des conflits :'), False, False, 5)
		box_conflicts = Gtk.VBox()
		scrolled = Gtk.ScrolledWindow()
		for i, fileinfo in enumerate(self.conflicts):  # self.conflicts = comparison['conflicts']
			# fileinfo [0]: filename
			# fileinfo [1]: tuple size
			# fileinfo [2]: tuple date
			box = Gtk.VBox()
			box.pack_start(Gtk.Label(fileinfo[0]), True, True, 5)

			date_local = datetime.datetime.fromtimestamp(fileinfo[2][0]).strftime('%c')
			local_text = 'Dans ' + self.paths[0] + ' , dernière modification : '
			local_text += date_local + ' , taille : ' + str(int(fileinfo[1][0])/1000) + ' Ko'
			radio_local = Gtk.RadioButton.new_with_label_from_widget(None, local_text)
			radio_local.connect("toggled", self.on_button_toggled, "local", i)

			date_ext = datetime.datetime.fromtimestamp(fileinfo[2][1]).strftime('%c')
			ext_text = 'Dans ' + self.paths[1] + ' , dernière modification : '
			ext_text += date_ext + ' , taille : ' + str(int(fileinfo[1][1])/1000) + ' Ko'
			radio_ext = Gtk.RadioButton.new_with_label_from_widget(radio_local, ext_text)
			radio_ext.connect("toggled", self.on_button_toggled, "ext", i)

			if fileinfo[2][0] > fileinfo[2][1]:  # local is more recent
				box.pack_start(radio_local, True, True, 1)
				box.pack_start(radio_ext, True, True, 1)
				radio_local.set_active(True)
			else:
				box.pack_start(radio_ext, True, True, 1)
				box.pack_start(radio_local, True, True, 1)
				radio_ext.set_active(True)

			box_conflicts.pack_start(box, True, True, 5)
			# end for
		scrolled.add(box_conflicts)
		self.box.pack_start(scrolled, True, True, 2)

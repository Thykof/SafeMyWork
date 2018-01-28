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

	def initialise_box(self):
		self.box.set_spacing(6)
		print('initialise_box')
		self.box.pack_start(Gtk.Label('Liste des conflits :'), False, False, 5)
		box_conflicts = Gtk.VBox()
		scrolled = Gtk.ScrolledWindow()
		for fileinfo in self.conflicts:
			# fileinfo [0]: filename
			# fileinfo [1]: tuple size
			# fileinfo [2]: tuple date
			box = Gtk.VBox()
			box.pack_start(Gtk.Label(fileinfo[0]), True, True, 5)

			date_local = datetime.date.fromtimestamp(fileinfo[2][0]).strftime('%c')
			local_text = 'Dans ' + self.paths[0] + ' , dernier accès : '
			local_text += date_local + ' , taille : ' + str(int(fileinfo[1][0])/1000) + ' Ko'
			radio_local = Gtk.RadioButton.new_with_label_from_widget(None, local_text)

			date_ext = datetime.date.fromtimestamp(fileinfo[2][1]).strftime('%c')
			ext_text = 'Dans ' + self.paths[1] + ' , dernier accès : '
			ext_text += date_ext + ' , taille : ' + str(int(fileinfo[1][1])/1000) + ' Ko'
			radio_ext = Gtk.RadioButton.new_with_label_from_widget(radio_local, ext_text)
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

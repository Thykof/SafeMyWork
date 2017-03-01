# -*- coding: utf-8 -*-
#!/usr/bin/python3

from os import path

from watcher import helpers

class BaseTestMod(object):
	def setup_method(self, test_method):
		pass

class TestMod(BaseTestMod):
	def test_combine_list(self):
		list1 = ['elt1', 'elt2']
		list2 = ['elt2', 'elt3']
		result = helpers.combine_list(list1, list2)
		assert result == ['elt2']

#!/usr/bin/python3

from safer import helpers

class BaseTest(object):
	def setup_method(self, test_method):
		pass

class TestHelpers(BaseTest):
	def test_combine_list(self):
		list1 = ['elt1', 'elt2']
		list2 = ['elt2', 'elt3']
		result = helpers.combine_list(list1, list2)
		assert result == ['elt2']

	def test_path_without_root(self):
		path = 'foo/bar'
		assert helpers.path_without_root(path) == 'bar'
		assert helpers.path_without_root('foo') == ''
		assert helpers.path_without_root('') == ''


	def test_missing_item(self):
		list1 = [1, 2, 3]
		list2 = [1, 2, 4]
		assert helpers.missing_item(list1, list2) == [3]
		assert helpers.missing_item([1], [2]) == [1]
		assert helpers.missing_item([], []) == []
		assert helpers.missing_item([], [1]) == []

	def test_split_path(self):
		path = '/home/user/documents/python/django/db/mysql'
		paths = helpers.split_path(path)
		assert paths == ['mysql', 'db', 'django', 'python', 'documents', 'user', 'home']

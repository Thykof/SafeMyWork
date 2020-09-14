#!/usr/bin/python3

from os import path


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
		p = path.join('foo', path.join('bar', 'jack'))
		assert helpers.path_without_root(p) == path.join('bar', 'jack')
		assert helpers.path_without_root('foo') == ''
		assert helpers.path_without_root('') == ''
		assert helpers.path_without_root(path.join('foo bar', 'jack')) == 'jack'


	def test_missing_item(self):
		list1 = [1, 2, 3]
		list2 = [1, 2, 4]
		assert helpers.missing_item(list1, list2) == [3]
		assert helpers.missing_item([1], [2]) == [1]
		assert helpers.missing_item([], []) == []
		assert helpers.missing_item([], [1]) == []

	def test_split_path(self):
		paths = helpers.split_path('/home/user/documents/python/django/db/mysql')
		assert paths == ['mysql', 'db', 'django', 'python', 'documents', 'user', 'home']

		paths = helpers.split_path('/home/user/my documents/python/django/db/mysql')
		assert paths == ['mysql', 'db', 'django', 'python', 'my documents', 'user', 'home']

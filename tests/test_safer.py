#!/usr/bin/python3

from safer import helpers, sync

class BaseTest(object):
	def setup_method(self, test_method):
		pass

class TestSafer(BaseTest):
	def _test_safer(self):
		path1 = '/home/thykof/Téléchargements'
		path2 = '/home/thykof/Vidéos'
		mysync = sync.Sync(path1, path2)
		errors = mysync.exec_sync()
		assert errors == (list(), list())

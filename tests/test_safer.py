#!/usr/bin/python3

from safer import helpers, scan, sync

class BaseTest(object):
	def setup_method(self, test_method):
		pass

class TestSafer(BaseTest):
    def _test_safer(self):
        path1 = '/home/thykof/Téléchargements'
        path2 = '/home/thykof/Vidéos'
        myscan = scan.Scan()
        files1 = myscan.scan_dir(path1)
        files2 = myscan.scan_dir(path2)
        mysync = sync.Sync(path1, path2)
        errors = mysync.run(files1, files2)
        assert errors == (list(), list())

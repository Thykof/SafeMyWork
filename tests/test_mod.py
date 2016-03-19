# -*- coding: utf-8 -*-
#!/usr/bin/python3

from os import path

from watcher import mod

class BaseTestMod(object):
    def setup_method(self, test_method):
        pass

class TestMod(BaseTestMod):
    def test_tell(self, tmpdir):
        test_message = 'This is a test.'
        test_output = 'test_output.log'
        target = tmpdir.join(test_output)
        mod.tell(test_message, target.strpath)
        content = target.read()
        assert content == test_message + '\n'

    def test_combine_list(self):
        list1 = ['elt1', 'elt2']
        list2 = ['elt2', 'elt3']
        result = mod.combine_list(list1, list2)
        assert result == ['elt2']

    def test_create_archive_dir(self, tmpdir):
        test_archive_dir = tmpdir.join('test_archive_dir')
        test_delicate_dir1 = tmpdir.join(path.join('test_archive_dir', 'test_delicate_dir1'))
        test_delicate_dir2 = tmpdir.join(path.join('test_archive_dir', 'test_delicate_dir2'))
        test_delicate_dirs = [test_delicate_dir1.strpath, test_delicate_dir2.strpath]

        mod.create_archive_dir(test_archive_dir.strpath, test_delicate_dirs)

        assert path.exists(test_archive_dir.strpath)
        assert path.exists(test_delicate_dir1.strpath)
        assert path.exists(test_delicate_dir2.strpath)

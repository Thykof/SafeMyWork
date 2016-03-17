# -*- coding: utf-8 -*-

from smw_core import watcher
from os import path, mkdir

class BaseTestWatcher(object):
    def setup_method(self, test_method):
        self.default_config = {
            'time_delta': 20,
            'archive_dir': 'safe_docs',
            'delicate_dirs': ["a_delicate_dir/folderA"],
            'exclude_dirs': ['a_delicate_dir/notthatfolder'],
            'exclude_files': ['a_delicate_dir/notthatfile.txt'],
            'exclude_ext': ['pdf', 'json']
        }
        self.config = self.default_config

class TestWatcher(BaseTestWatcher):
    def test_start(self):
        pass

    def test_list_files(self, tmpdir):
        # Create all files:
        folderA = tmpdir.join('a_delicate_dir')
        test_folderA = folderA.strpath
        file1 = tmpdir.join(path.join('a_delicate_dir', 'notthatfile.txt'))
        test_file1 = file1.strpath

        mkdir(test_folderA)
        open(test_file1, 'w').close()

        files = watcher.Watcher.list_files(self, test_folderA)
        assert files == ['notthatfile.txt']

    def test_list_files(self, tmpdir):
        # Create all files:
        folderA = tmpdir.join('a_delicate_dir')
        test_folderA = folderA.strpath
        folderB = tmpdir.join(path.join('a_delicate_dir', 'notthatfolder'))
        test_folderB = folderB.strpath

        mkdir(test_folderA)
        mkdir(test_folderB)

        files = watcher.Watcher.list_dirs(self, test_folderA)
        assert files == ['notthatfolder']

    def test_filter_files(self):
        assert watcher.Watcher.filter_files(self, 'a_delicate_dir/doc.txt')
        assert not watcher.Watcher.filter_files(self, 'a_delicate_dir/doc.pdf')
        assert not watcher.Watcher.filter_files(self, 'a_delicate_dir/notthatfile.txt')
        assert not watcher.Watcher.filter_files(self, 'a_delicate_dir/notthatfolder/file.txt')

    def test_compare_files(self):
        pass

    def test_create_safe_dirs(self, tmpdir):
        pass

    def test_archive_file(self, tmpdir):
        pass

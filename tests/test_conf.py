# -*- coding: utf-8 -*-

from smw_core import conf

class BaseTestConf(object):
    def setup_method(self, test_method):
        self.default_config = {
            'time_delta': 20,
            'archive_dir': 'safe_docs',
            'delicate_dirs': ["a_delicate_dir/folderA"],
            'exclude_dirs': ['a_delicate_dir/notthatfolder'],
            'exclude_files': ['a_delicate_dir/notthatfile.txt'],
            'exclude_ext': ['pdf', 'JSON']
        }

class TestConf(BaseTestConf):
    def test_save_config(self):
        conf.save_config(self.default_config)

    def test_read_config(self):
        config = conf.read_config()
        assert config['time_delta'] == 20
        assert config['exclude_ext'] == ['pdf', 'json']

    def test_get_dir_from_argv(self):
        assert conf.get_dir_from_argv(['main.py']) == []
        argv = ['main.py', 'docs', 'unexisting_dir']
        dirs = conf.get_dir_from_argv(argv)
        assert dirs == ['docs']

    def test_get_config(self):
        conf.get_config()

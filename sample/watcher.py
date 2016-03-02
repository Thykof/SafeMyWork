# -*- coding: utf-8 -*-

from os import path, walk, stat
from glob import glob
from .mod import tell, combine_list
from time import time, sleep

class Watcher(object):
    """docstring for Watcher"""
    def __init__(self, directory, config):
        super(Watcher, self).__init__()
        self.DIR = directory  # Directory watch
        self.archive_dir = config['archive_dir']

    def start(self):
        while True:
            tell('Watching...')
            files = self.list_files(self.DIR)
            print(files)
            to_save = self.compare_files(files)
            for filename in to_save:
                self.archive_file(filename)

            break  # Dev

    def list_files(self, directory):
        """Return list of files in given dir.

        Each filenames begin with '/'.

        """
        list_files = list()
        for root, directories, files in walk(directory):
            for filenames in files:
                filename = path.join(root, filenames)
                position = filename.find('/')
                list_files.append(filename[position:])
        return list_files

    def compare_files(self, unsaved_files):
        """Return a list of files need to save."""
        saved_files = self.list_files(self.archive_dir)
        print(self.archive_dir, saved_files)
        files_to_save = list()
        if unsaved_files != saved_files:
            for unsaved_file in unsaved_files:
                if unsaved_file not in saved_files:
                    files_to_save.append(unsaved_file)
                    tell('Add: ' + unsaved_file)

        list_files = combine_list(unsaved_files, saved_files)
        for filename in list_files:
            saved_file_stat = stat(self.archive_dir + filename)
            unsaved_file_stat = stat(self.DIR + filename)
            if saved_file_stat.st_mtime < unsaved_file_stat.st_mtime:
                files_to_save.append(filename)
                tell('Update: ' + filename)
            elif saved_file_stat.st_mtime > unsaved_file_stat.st_mtime:
                tell('Saved file have been modified !')
            else:
                tell('Skipping ' + filename)
        return files_to_save

    def archive_file(self, file):
        pass

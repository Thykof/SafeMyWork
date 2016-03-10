# -*- coding: utf-8 -*-

from os import path, walk, stat, mkdir
from glob import glob
from .mod import tell, combine_list
from time import sleep
import shutil

class Watcher(object):
    def __init__(self, directory, config):
        super(Watcher, self).__init__()
        self.delicate_dir = directory  # Directory watch
        self.archive_dir = config['archive_dir']

    def start(self):
        """Start watching."""
        while True:
            tell('===WATCHING===')
            for delicate_dir in self.delicate_dir:
                unsaved_files = self.list_files(delicate_dir)
                saved_files = self.list_files(path.join(self.archive_dir, delicate_dir))
                files_to_save = self.compare_files(unsaved_files, saved_files, delicate_dir)
                for filename in files_to_save:
                    self.archive_file(filename, delicate_dir)

            sleep(15)  # 15s for develop branch

    def list_files(self, delicate_dir):
        """Return list of files in given dir.

        Each filenames begin with '/'.

        """
        list_files = list()
        for root, directories, files in walk(delicate_dir):
            for filenames in files:
                filename = path.join(root, filenames)
                position = len(delicate_dir)
                list_files.append(filename[position+1:])
        return list_files

    def compare_files(self, unsaved_files, saved_files, delicate_dir):
        """Return a list of files need to save."""
        files_to_save = list()
        if unsaved_files != saved_files:
            for unsaved_file in unsaved_files:
                if unsaved_file not in saved_files:
                    files_to_save.append(unsaved_file)
                    tell('Add: ' + unsaved_file)

        list_files = combine_list(unsaved_files, saved_files)
        for filename in list_files:
            saved_file_stat = stat(path.join(self.archive_dir, delicate_dir, filename))
            unsaved_file_stat = stat(path.join(delicate_dir, filename))
            if saved_file_stat.st_mtime < unsaved_file_stat.st_mtime:
                files_to_save.append(filename)
                tell('Update: ' + filename)
            elif saved_file_stat.st_mtime > unsaved_file_stat.st_mtime:
                tell('Saved file have been modified !')
            else:
                tell('Skipping ' + filename)
        return files_to_save

    def archive_file(self, filename, delicate_dir):
        """Copy the file arg in the archive directory."""
        for root, directories, files in walk(delicate_dir):
            folder = path.join(self.archive_dir, root)
            if not path.exists(folder):
                mkdir(folder)

        archived_file = shutil.copy2(path.join(delicate_dir, filename), path.join(self.archive_dir, delicate_dir, filename))

        tell('Archived: ' + archived_file)

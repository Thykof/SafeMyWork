# -*- coding: utf-8 -*-

from os import path, walk, stat, mkdir
from time import sleep
import shutil

from smw_core import mod

class Watcher(object):
    def __init__(self, config):
        super(Watcher, self).__init__()
        self.config = config
        self.delicate_dir = config['delicate_dirs']  # Directory watch
        self.archive_dir = config['archive_dir']

        mod.create_archive_dir(self.archive_dir, self.delicate_dir)

    def start(self):
        """Start watching."""
        while True:
            mod.tell('===WATCHING===')
            for delicate_dir in self.delicate_dir:
                unsaved_files = self.list_files(delicate_dir)
                saved_files = self.list_files(path.join(self.archive_dir, path.basename(delicate_dir)))
                files_to_save = self.compare_files(unsaved_files, saved_files, delicate_dir)
                if len(files_to_save) > 0:
                    self.create_safe_dirs(delicate_dir)
                    for filename in files_to_save:
                        self.archive_file(filename, delicate_dir)

            break
            sleep(self.config['time_delta'])

    def list_files(self, path_dir):
        """Return list of files in the given path."""
        list_files = list()
        for root, directories, files in walk(path_dir):
            for filenames in files:
                filename = path.join(root, filenames)
                position = len(path_dir)
                list_files.append(filename[position+1:])
        return list_files

    def list_dirs(self, path_dir):
        """Return list of directories in the given path."""
        list_dirs = list()
        for root, directories, files in walk(path_dir):
            for directory in directories:
                delicate_dir = path.join(root, directory)
                position = len(path_dir)
                list_dirs.append(delicate_dir[position+1:])
        return list_dirs

    def compare_files(self, unsaved_files, saved_files, delicate_dir):
        """Return a list of files need to save."""
        files_to_save = list()
        if unsaved_files != saved_files:
            for unsaved_file in unsaved_files:
                if unsaved_file not in saved_files:
                    files_to_save.append(unsaved_file)
                    mod.tell('Add: ' + unsaved_file)

        list_files = mod.combine_list(unsaved_files, saved_files)
        for filename in list_files:
            saved_file_stat = stat(path.join(self.archive_dir, delicate_dir, filename))
            unsaved_file_stat = stat(path.join(delicate_dir, filename))
            if saved_file_stat.st_mtime < unsaved_file_stat.st_mtime:
                files_to_save.append(filename)
                mod.tell('Update: ' + filename)
            elif saved_file_stat.st_mtime > unsaved_file_stat.st_mtime:
                mod.tell('Saved file have been modified !')
            else:
                mod.tell('Skipping ' + filename)
        return files_to_save

    def create_safe_dirs(self, delicate_dir):
        """Make all directories from delicate dir in archive dir."""
        dirs = self.list_dirs(delicate_dir)
        for directory in dirs:
            path_dir = path.join(self.archive_dir, path.basename(delicate_dir), directory)
            if not path.exists(path_dir):
                mkdir(path_dir)


    def archive_file(self, filename, delicate_dir):
        """Copy the file arg in the archive directory."""
        src = path.join(delicate_dir, filename)
        dst = path.join(self.archive_dir, path.basename(delicate_dir), filename)
        archived_file = shutil.copy2(src, dst)
        mod.tell('Archived: ' + archived_file)

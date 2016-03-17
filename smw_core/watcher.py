# -*- coding: utf-8 -*-

from os import path, walk, stat, mkdir
from time import sleep
import shutil

from smw_core import mod

class Watcher(object):
    """A class that manage safing files."""
    def __init__(self, config):
        super(Watcher, self).__init__()
        self.config = config
        self.delicate_dir = config['delicate_dirs']  # Directory watch
        self.archive_dir = config['archive_dir']

        mod.create_archive_dir(self.archive_dir, self.delicate_dir)

    def start(self):
        """Start **watching**.

        - list unsaved files
        - list saved files
        - compare them
        - archive the new files
        - wait for the *time_delta* setting
        """
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

            mod.tell('Done')
            sleep(self.config['time_delta'])

    def list_files(self, path_dir):
        """List all files in the given *path_dir*.

        :param path_dir: the path of the directory.
        :type path_dir: ``str``
        :returns: the list of files
        :rtype: ``list``
        """
        list_files = list()
        for root, directories, files in walk(path_dir):
            for filenames in files:
                filename = path.join(root, filenames)
                position = len(path_dir)
                list_files.append(filename[position+1:])
        return list_files

    def list_dirs(self, path_dir):
        """List all directories in the given *path_dir*.

        .. seealso::
            Like :func:`list_files`
        """
        list_dirs = list()
        for root, directories, files in walk(path_dir):
            for directory in directories:
                delicate_dir = path.join(root, directory)
                position = len(path_dir)
                list_dirs.append(delicate_dir[position+1:])
        return list_dirs

    def filter_files(self, filename):
        """Return ``True`` if *filename* must be archive.

        :param filename: the filename
        :type filename: ``str``
        :returns: ``True`` or ``False``
        :rtype: ``bool``
        """
        # Filter extension:
        ext_pos = filename.rfind('.')
        ext = filename[ext_pos+1:].lower()
        ext_ok = False if ext in self.config['exclude_ext'] else True
        # Filter files:
        file_ok = False if filename in self.config['exclude_files'] else True
        # Filter directories:
        directory = path.split(filename)[0]
        dir_ok = False if directory in self.config['exclude_dirs'] else True

        if ext_ok and file_ok and dir_ok:
            return True
        else:
            mod.tell('Exclude: ' + filename)
            return False

    def compare_files(self, unsaved_files, saved_files, delicate_dir):
        """List all files that need to be save.

        :param unsaved_files: the unsaved files
        :type unsaved_files: ``list``
        :param saved_files: the files already saved
        :type saved_files: ``list``
        :param delicate_dir: the directory watching
        :type delicate_dir: ``str``
        :returns: the files need to ba save
        :rtype: ``list``
        """
        files_to_save = list()
        if unsaved_files != saved_files:
            for unsaved_file in unsaved_files:
                if unsaved_file not in saved_files:
                    if self.filter_files(unsaved_file):
                        mod.tell('Add: ' + unsaved_file)
                        files_to_save.append(unsaved_file)

        list_files = mod.combine_list(unsaved_files, saved_files)
        for filename in list_files:
            saved_file_stat = stat(path.join(self.archive_dir, delicate_dir, filename))
            unsaved_file_stat = stat(path.join(delicate_dir, filename))
            if saved_file_stat.st_mtime < unsaved_file_stat.st_mtime:
                if self.filter_files(filename):
                    mod.tell('Update: ' + filename)
                    files_to_save.append(filename)
            elif saved_file_stat.st_mtime > unsaved_file_stat.st_mtime:
                mod.tell('Saved file have been modified !')
            else:
                mod.tell('Skipping: ' + filename)
        return files_to_save

    def create_safe_dirs(self, delicate_dir):
        """Make all directories from *delicate_dir* in archive directory.

        :param delicate_dir: the directory watching
        :type delicate_dir: ``str``
        """
        dirs = self.list_dirs(delicate_dir)
        for directory in dirs:
            path_dir = path.join(self.archive_dir, path.basename(delicate_dir), directory)
            if not path.exists(path_dir):
                mkdir(path_dir)

    def archive_file(self, filename, delicate_dir):
        """Copy the *filename* in the archive directory.

        :param filename: filename of the file to save
        :type filename: ``str``
        :param delicate_dir: the directory watching
        :type delicate_dir: ``str``
        """
        src = path.join(delicate_dir, filename)
        dst = path.join(self.archive_dir, path.basename(delicate_dir), filename)
        archived_file = shutil.copy2(src, dst)
        mod.tell('Archived: ' + archived_file)

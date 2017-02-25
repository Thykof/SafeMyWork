# -*- coding: utf-8 -*-
#!/usr/bin/python3

from os import path, walk, stat, mkdir
import shutil

from .mod import tell, create_archive_dir, combine_list

class Watcher(object):
    """A class that manage safing files."""
    def __init__(self, config):
        super(Watcher, self).__init__()
        self.stop = False
        self.config = config

    def watch(self):
        """Start **watching**.

        - list unsaved files
        - list saved files
        - compare them
        - archive the new files
        - wait for the *time_delta* setting
        """
        create_archive_dir(self.config['archive_dir'], self.config['watched_dirs'])
        tell('===WATCHING===')
        for watched_dir in self.config['watched_dirs']:
            if not self.stop:
                unsaved_files = self.list_files(watched_dir)
                saved_files = self.list_files(path.join(self.config['archive_dir'], path.basename(watched_dir)))
                files_to_save = self.compare_files(unsaved_files, saved_files, watched_dir)
                if len(files_to_save) > 0:
                    self.create_safe_dirs(watched_dir, files_to_save)
                    for filename in files_to_save:
                        if not self.stop:
                            archived_file = self.archive_file(filename, watched_dir)
                            tell('Archived: ' + archived_file)
                        else:
                            break
            else:
                break
            tell('Done')

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
                watched_dir = path.join(root, directory)
                position = len(path_dir)
                list_dirs.append(watched_dir[position+1:])
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
        dir_ok = True
        directory = path.dirname(filename)
        for exclude_dir in self.config['exclude_dirs']:
            if exclude_dir in directory:
                dir_ok = False
        if directory is '':
            dir_ok = True

        if ext_ok and file_ok and dir_ok:
            return True
        else:
            return False

    def compare_files(self, unsaved_files, saved_files, watched_dir):
        """List all files that need to be save.

        :param unsaved_files: the unsaved files
        :type unsaved_files: ``list``
        :param saved_files: the files already saved
        :type saved_files: ``list``
        :param watched_dir: the directory watching
        :type watched_dir: ``str``
        :returns: the files need to ba save
        :rtype: ``list``
        """
        files_to_save = list()
        # new files in files_to_save:
        if unsaved_files != saved_files:
            for unsaved_file in unsaved_files:
                if unsaved_file not in saved_files:
                    if self.filter_files(unsaved_file):
                        tell('Add: ' + unsaved_file)
                        files_to_save.append(unsaved_file)
                    else:
                        tell('Exclude: ' + unsaved_file)

        list_files = combine_list(unsaved_files, saved_files)
        for filename in list_files:
            saved_file_stat = stat(path.join(self.config['archive_dir'], watched_dir, filename))
            unsaved_file_stat = stat(path.join(watched_dir, filename))
            if saved_file_stat.st_mtime < unsaved_file_stat.st_mtime:
                if self.filter_files(filename):
                    tell('Update: ' + filename)
                    files_to_save.append(filename)
                else:
                    tell('Exclude: ' + filename)
            elif saved_file_stat.st_mtime > unsaved_file_stat.st_mtime:
                tell('Saved file have been modified !')
            else:
                tell('Skipping: ' + filename)
        return files_to_save

    def create_safe_dirs(self, watched_dir, files_to_save):
        """Make all directories from *watched_dir* in archive directory.

        :param watched_dir: the directory watching
        :type watched_dir: ``str``
        """
        dirs = self.list_dirs(watched_dir)
        for directory in dirs:
            # Don't create directory excluded:
            exclude_dir = True
            # Same var name !? exclude_dir
            for exclude_dir in self.config['exclude_dirs']:
                if exclude_dir in directory:
                    exclude_dir = False
            if exclude_dir:
                path_dir = path.join(self.config['archive_dir'], path.basename(watched_dir), directory)
                if not path.exists(path_dir):
                    mkdir(path_dir)

    def archive_file(self, filename, watched_dir):
        """Copy the *filename* in the archive directory.

        :param filename: filename of the file to save
        :type filename: ``str``
        :param watched_dir: the directory watching
        :type watched_dir: ``str``
        """
        src = path.join(watched_dir, filename)
        dst = path.join(self.config['archive_dir'], path.basename(watched_dir), filename)
        archived_file = shutil.copy2(src, dst)
        return archived_file

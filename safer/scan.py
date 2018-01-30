#!/usr/bin/python3

from os import chdir, path, walk

from safer.helpers import split_path, path_without_root, store


class Scan(object):
    def __init__(self):
        super(Scan, self).__init__()
        self.stop = False

        self.config = dict()
        self.config['dirname'] = list()
        self.config['dirpath'] = list()
        self.config['filename'] = list()
        self.config['extention'] = list()

        self.safe_doc = path.join(path.expanduser('~'), 'safe_docs')

    def set_safe_doc(self, safe_doc):
        self.safe_doc = safe_doc

    def scan_dir(self, dirname):
        list_files = list()  # List of relatif path to each file
        chdir(path.dirname(dirname))
        walked_dir = path.basename(dirname)
        for info in walk(walked_dir):  # walk() return a generator
            dirpath, filenames = info[0], info[2]
            # dirpath = dirname, for the first time
            # dirpath = subdirs of dirname
            if self.stop:
                break

            # Exclude a dirname name
            can = True
            for dirname in split_path(dirpath):
                if dirname in self.config['dirname']:
                    can = False

            # Exclude a path
            can = True
            for dirname in self.config['dirpath']:
                if dirpath.find(dirname) != -1:
                    can = False
            if can:
                dirname = path_without_root(dirpath)
                # Take all files
                for filename in filenames:
                    # Find the extension
                    ext = path.splitext(filename)[1][1:]
                    if filename not in self.config['filename'] and ext not in self.config['extention']:
                        list_files.append(path.join(dirname, filename))
                    if self.stop:
                        break

        json_filename = 'analysisW' + '_'.join(dirname.split('/')) + '.json'
        store(list_files, self.safe_doc, json_filename)
        return list_files

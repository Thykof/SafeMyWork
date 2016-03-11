# -*- coding: utf-8 -*-

"""Monitoring configuration variables."""

from os import path
import sys
import json

from .data import FILE_CONFIG, INT_VALUES, DEFAULT_CONFIG
from .mod import tell

def read_config():
    with open(FILE_CONFIG, 'r') as configfile:
        values = json.load(configfile)
    for key in values.keys():
        if key in INT_VALUES:
            values[key] == int(values[key])
    return values

def save_config(values=DEFAULT_CONFIG):
    tell('Saving config')
    with open(FILE_CONFIG, 'w') as configfile:
        json.dump(values, configfile, indent=4)

def get_dir_from_argv():
    """Return dir to watch.

    Return a list, only existing directories.
    """
    if len(sys.argv) == 1:
        return []
    else:
        delicate_dirs = list()
        for directory in sys.argv[1:]:
            if path.exists(directory):
                delicate_dirs.append(directory)
        return delicate_dirs

def get_config():
    if not path.exists(FILE_CONFIG):
        save_config()
        tell('No delicate directory')
        sys.exit()
    else:
        config = read_config()
        delicate_dirs = get_dir_from_argv()
        config['delicate_dirs'].extend(delicate_dirs)
        if config['delicate_dirs'] == []:
            tell('No delicate directory')
            sys.exit()

    return config

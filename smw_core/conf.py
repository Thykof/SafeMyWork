# -*- coding: utf-8 -*-

"""Monitoring configuration variables."""

from os import path
import sys
import json

from .data import FILE_CONFIG, INT_VALUES, DEFAULT_CONFIG
from .mod import tell

def read_config():
    """Read the configuration file using :mod:`json`.

    Convert the *time_delta* setting.
    Lower case extensions.

    :returns: settings
    :rtype: ``dict``
    """
    with open(FILE_CONFIG, 'r') as configfile:
        config = json.load(configfile)
    # Convert keys:
    for key in config.keys():
        if key in INT_VALUES:
            config[key] == int(config[key])
    # Lower extensions:
    list_ext = list()
    for ext in config['exclude_ext']:
        list_ext.append(ext.lower())
    config['exclude_ext'] = list_ext
    return config

def save_config(config=DEFAULT_CONFIG):
    """Save the settings in the configurations file using :mod:`json`.

    :param config: settings
    :type config: ``dict``
    """
    tell('Saving config')
    with open(FILE_CONFIG, 'w') as configfile:
        json.dump(config, configfile, indent=4)

def get_dir_from_argv(argv=sys.argv):
    """Get the directory to watch from command line arguments.

    :param argv: default to sys.argv, given for tests
    :type argv: ``list``
    :returns: Existing directories
    :rype: ``list``
    """
    if len(argv) == 1:
        return []
    else:
        delicate_dirs = list()
        for directory in argv[1:]:
            if path.exists(directory):
                delicate_dirs.append(directory)
        return delicate_dirs

def get_config():
    """Manage getting settings.

    Searche for the configurations file.
    Create if it doesn't exists.
    Use :func:`get_dir_from_argv`.

    :returns: settings
    :rtype: ``dict``
    """
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

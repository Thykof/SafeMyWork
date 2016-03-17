# -*- coding: utf-8 -*-

"""Monitoring configuration variables."""

from os import path
import sys
import json

from .data import CONF_FILE, INT_VALUES, DEFAULT_CONFIG
from .mod import tell

def read_config(conf_file=CONF_FILE):
    """Read the configuration file using :mod:`json`.

    Convert the *time_delta* setting.
    Lower case extensions.

    :param conf_file: the configuration file
    :type conf_file: ``str``
    :returns: settings
    :rtype: ``dict``
    """
    with open(conf_file, 'r') as configfile:
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

def save_config(config=DEFAULT_CONFIG, conf_file=CONF_FILE):
    """Save the settings in the configurations file using :mod:`json`.

    :param config: settings
    :type config: ``dict``
    :param conf_file: the configuration file
    :type conf_file: ``str``
    """
    tell('Saving config')
    with open(conf_file, 'w') as configfile:
        json.dump(config, configfile, indent=4)

def get_dir_from_argv(argv=sys.argv):
    """Get the directory to watch from command line arguments.

    :param argv: default to sys.argv, given for tests
    :type argv: ``list``
    :returns: existing directories
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

def get_config(conf_file=CONF_FILE):
    """Manage getting settings.

    Searche for the configurations file.
    Create if it doesn't exists.
    Use :func:`get_dir_from_argv`.

    :param conf_file: the configuration file
    :type conf_file: ``str``
    :returns: settings
    :rtype: ``dict``
    """
    if not path.exists(conf_file):
        save_config(conf_file=conf_file)
        tell('No delicate directory')
        sys.exit()
    else:
        config = read_config(conf_file)
        delicate_dirs = get_dir_from_argv()
        config['delicate_dirs'].extend(delicate_dirs)
        if config['delicate_dirs'] == []:
            tell('No delicate directory')
            sys.exit()

    return config

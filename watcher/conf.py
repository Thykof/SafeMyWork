# -*- coding: utf-8 -*-
#!/usr/bin/python3

"""Monitoring configuration variables."""

from os import path
import sys
import json

from .data import CONF_FILE, DEFAULT_CONFIG

def read_config(conf_file=CONF_FILE):
    """Read the configuration file using :mod:`json`.

    Lower case extensions.

    :param conf_file: the configuration file
    :type conf_file: ``str``
    :returns: settings
    :rtype: ``dict``
    """
    with open(conf_file, 'r') as configfile:
        config = json.load(configfile)
    # Lower extensions:
    list_ext = list()
    for ext in config['exclude_ext']:
        list_ext.append(ext.lower())
    config['exclude_ext'] = list_ext
    return config

def save_config(config=None, conf_file=CONF_FILE):
    """Save the settings in the configurations file using :mod:`json`.

    :param config: settings
    :type config: ``dict``
    :param conf_file: the configuration file
    :type conf_file: ``str``
    """
    if config is None:
        config = DEFAULT_CONFIG
    with open(conf_file, 'w') as configfile:
        json.dump(config, configfile, indent=4)

def get_dir_from_argv(argv=None):
    """Get the directory to watch from command line arguments.

    :param argv: default to sys.argv, given for tests
    :type argv: ``list``
    :returns: existing directories
    :rype: ``list``
    """
    if argv is None:
        argv = sys.argv
    if len(argv) == 1:
        return []
    else:
        watched_dirs = list()
        for directory in argv[1:]:
            if path.exists(directory):
                watched_dirs.append(directory)
        return watched_dirs

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
        return DEFAULT_CONFIG
    else:
        config = read_config(conf_file)
        watched_dirs = get_dir_from_argv()
        config['watched_dirs'].extend(watched_dirs)
    return config

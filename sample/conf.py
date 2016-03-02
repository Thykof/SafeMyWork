# -*- coding: utf-8 -*-

"""Monitoring configuration variables.

tiemdaelt: default to 5sec, the time to sleep betwen each scan.

"""

from os import path
import json

from .data import FILE_CONFIG, INT_VALUES

def read_config():
    with open(FILE_CONFIG, 'r') as configfile:
        values = json.load(configfile)
    for key in values.keys():
        if key in INT_VALUES:
            values[key] == int(values[key])
    return values

def save_config(values={'timedelta': 5, 'archive_dir': 'safe_docs'}):
    with open(FILE_CONFIG, 'w') as configfile:
        json.dump(values, configfile)

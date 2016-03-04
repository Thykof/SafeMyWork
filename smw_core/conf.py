# -*- coding: utf-8 -*-

"""Monitoring configuration variables."""

from os import path
import json

from .data import FILE_CONFIG, INT_VALUES, DEFAULT_CONFIG

def read_config():
    with open(FILE_CONFIG, 'r') as configfile:
        values = json.load(configfile)
    for key in values.keys():
        if key in INT_VALUES:
            values[key] == int(values[key])
    return values

def save_config(values=DEFAULT_CONFIG):
    with open(FILE_CONFIG, 'w') as configfile:
        json.dump(values, configfile)

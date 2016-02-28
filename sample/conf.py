# -*- coding: utf-8 -*-

"""Monitoring configuration variables.

tiemdaelt: default to 5sec, the time to sleep betwen each scan.

"""

from os import path
from configparser import ConfigParser

import data

def creat_conf(values={'timedelta': 5}):
    config = ConfigParser()
    for key in values.keys():
        config['DEFAULT'] = {key: values[key]}
    with open(FILE_CONFIG, 'w') as configfile:
        config.write(configfile)

def read_config():
    values = dict()
    with open(data.FILE_CONFIG, 'r') as configfile:
        config.read(configfile)
        values['imedelta'] = config['DEFAULT']['timedelta']
    return values

def save_config(values):
    config['DEFAULT'] = {'timedelta': values['timedelta']}
    with open(data.FILE_CONFIG, 'w') as configfile:
        config.write(configfile)

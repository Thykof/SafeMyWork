# -*- coding: utf-8 -*-

import sys

myfile = open('stderr.log', 'a')
sys.stderr = myfile

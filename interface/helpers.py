#!/usr/bin/python3

from platform import system
SYSTEM = system()
if SYSTEM == 'Linux':
	from subprocess import Popen
elif SYSTEM == 'Windows':
	from os import startfile
else:
	print('Import Error: system')

def open_folder(_, folder_name):
    """Open in nautilus or file explorer, in the safe directory."""
    if folder_name != '':
        if SYSTEM == 'Linux':
            Popen(['xdg-open', folder_name])
        elif SYSTEM == 'Windows':
            startfile(folder_name)

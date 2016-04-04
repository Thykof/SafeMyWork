# -*- coding: utf-8 -*-
#!/usr/bin/python3

import site
import sys
import os

from cx_Freeze import setup, Executable

# This is a list of files that cx_freeze includes in the build. Each
# entry is a tuple of source and destination.
include_files = []

# Usually C:\Python34\lib\site-packages\gnome
gnome_dir = os.path.join(site.getsitepackages()[1], "gnome")

# Required Gnome DLLs
gnome_dlls = ['libatk-1.0-0.dll',
              'libcairo-gobject-2.dll',
              'libffi-6.dll',
              'libfontconfig-1.dll',
              'libfreetype-6.dll',
              'libgdk-3-0.dll',
              'libgdk_pixbuf-2.0-0.dll',
              'libgio-2.0-0.dll',
              'libgirepository-1.0-1.dll',
              'libglib-2.0-0.dll',
              'libgmodule-2.0-0.dll',
              'libgobject-2.0-0.dll',
              'libgstapp-1.0-0.dll',
              'libgstaudio-1.0-0.dll',
              'libgstbase-1.0-0.dll',
              'libgstcontroller-1.0-0.dll',
              'libgstfft-1.0-0.dll',
              'libgstnet-1.0-0.dll',
              'libgstpbutils-1.0-0.dll',
              'libgstreamer-1.0-0.dll',
              'libgstriff-1.0-0.dll',
              'libgstrtp-1.0-0.dll',
              'libgstrtsp-1.0-0.dll',
              'libgstsdp-1.0-0.dll',
              'libgsttag-1.0-0.dll',
              'libgstvideo-1.0-0.dll',
              'libgtk-3-0.dll',
              'libharfbuzz-gobject-0.dll',
              'libintl-8.dll',
              'libjasper-1.dll',
              'libjpeg-8.dll',
              'liborc-0.4-0.dll',
              'liborc-test-0.4-0.dll',
              'libp11-kit-0.dll',
              'libpango-1.0-0.dll',
              'libpangocairo-1.0-0.dll',
              'libpangoft2-1.0-0.dll',
              'libpangowin32-1.0-0.dll','libpng16-16.dll',
              'libproxy.dll',
              'librsvg-2-2.dll',
              'libsoup-2.4-1.dll',
              'libsqlite3-0.dll',
              'libvisual-0.4-0.dll',
              'libwebp-5.dll',
              'libwinpthread-1.dll',
              'libxmlxpat.dll',
              'libzzz.dll',
              'libepoxy-0.dll',
              'libharfbuzz-0.dll',
              'libtiff-5.dll'
]
for dll in gnome_dlls:
    include_files.append((os.path.join(gnome_dir, dll), dll))

# We need some more Gnome files (theme, icons, translation, ...).
gnome_folders = ['etc\\fonts',
                 'etc\\gtk-3.0',
                 'lib\\girepository-1.0',
                 'lib\\gstreamer-1.0',
                 'share\\glib-2.0',
                 'share\\icons\\Adwaita',
                 'share\\icons\\hicolor',
                 'share\\locale\\de',
                 'share\\locale\\en',
]
for folder in gnome_folders:
    include_files.append((os.path.join(gnome_dir, folder), folder))
include_files.append((os.path.join(gnome_dir, 'license'), 'license-gnome'))

base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [Executable("SafeMyWork.py", base=base)]

build_options = {
    'build_exe': 'build',
    'compressed': False,
    'includes': 'gi',
    'packages': 'gi',
    'include_files': include_files
}

setup(
    name = "SafeMyWork",
    author = "Thykof",
    version = "1.0",
    description = "Autosave your work",
    options = dict(build_exe = build_options),
    executables = executables
)

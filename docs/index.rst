.. SafeMyWork documentation master file, created by
   sphinx-quickstart on Sat Mar 12 19:09:42 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to SafeMyWork's documentation!
**************************************
The current version is 0.6.1.

https://github.com/Thykof/SafeMyWork

SafeMyWork is intended for people who handle a lot of files which can be texts,
images, songs... The aim is to **avoid losing** documents.

How it works
============
SafeMyWork looks for your modified files and copies them to another directory.
The second feature is the synchronization of two folders.

Automatic saving
================
Run SafeMyWork and select your working folders. Then while you are working,
every a certain amount of time, all files in this folder will be copied into a
separate folder. It keeps your files safe if you forget to save your work or
delete accidentally files.

Synchronization
===============
The application can synchronize two folders. After scanning the two folders
selected by the user, a dialog message shows potential conflicts. A conflict
occurs when a file has the same path and the same name in both folders. The user
selects the file that she/he wants to keep. The size of the files and the last
modification time are shown to help the choose. Then, a dialog shows what files
would be lost (conflict resolution) and what files would be created (missing
files in a folder).


Safer: save files
=================
.. autoclass:: safer.safe.Safer
  :members:
  :undoc-members:

Sync: synchronize folders
=========================
.. autoclass:: safer.sync.Sync
  :members:
  :undoc-members:

A module for simple functions
+++++++++++++++++++++++++++++
.. automodule:: safer.helpers
  :members:

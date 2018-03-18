.. SafeMyWork documentation master file, created by
   sphinx-quickstart on Sat Mar 12 19:09:42 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to SafeMyWork's documentation!
**************************************

https://github.com/Thykof/SafeMyWork

SafeMyWork is intend for people who handle lot of files which can be texts,
images, songs... The aim is to **avoid losing** documents.

How it work
===========
SafeMyWork look for your modified files and copy them to another directory.
The second feature is synchronisation of two folders.

Automitic saving
================
Run SafeMyWork and select your working folders. Then while you are working,
every a certain amount of time, all files in this folder will be copying into a
separated folder. It keeps your files safe if you forget to save your work or
delete accidentally files.

Synchronization
===============
The application can synchronize two folders. After scanning the two folders
selected by the user, a dialog message shows potential conflicts. A conflict
occurs when a file has the same path and same name in both folders. The user
selects the file that she/he wants to keep. The size of the files and the last
modification time are shown to help the choose. Then, a dialog shows what files
would be lost (conflict resolution) and what files would be create (missing
files in a folder).


Safer: save files
=================
.. autoclass:: safer.safe.Safer
  :members:
  :undoc-members:

Sync: synchronise folders
=========================
.. autoclass:: safer.sync.Sync
  :members:
  :undoc-members:

A module for simple functions
+++++++++++++++++++++++++++++
.. automodule:: safer.helpers
  :members:

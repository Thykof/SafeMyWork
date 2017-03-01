.. SafeMyWork documentation master file, created by
   sphinx-quickstart on Sat Mar 12 19:09:42 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to SafeMyWork's documentation!
**************************************

.. image:: https://readthedocs.org/projects/safemywork/badge/?version=develop
  :target: http://safemywork.readthedocs.org/en/develop
  :alt: Documentation Status

How it work
===========
SafeMyWork look for your modified files and copy them to another directory.

Launch the app
++++++++++++++
.. automodule:: main
  :members:
  :undoc-members:

Safer: save files
=================
.. autoclass:: watcher.safe.Safer
  :members:
  :undoc-members:

A module for simple functions
+++++++++++++++++++++++++++++
.. automodule:: watcher.helpers
  :members:

Interface
=========
.. autoclass:: interface.interface.MyWindow
  :members:

Dialog
++++++
.. automodule:: interface.dialog
  :members:

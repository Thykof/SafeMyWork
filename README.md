# Safe My work
SafeMyWork saves all files in the given directory into another directory to keep your work safe and avoid losing data and time.

[![Documentation Status](https://readthedocs.org/projects/safemywork/badge/?version=master)](http://safemywork.readthedocs.io/en/master/?badge=master)
[![Build Status](https://travis-ci.org/Thykof/SafeMyWork.svg?branch=master)](https://travis-ci.org/Thykof/SafeMyWork)

## What for?
SafeMyWork is intended for people who **handle a lot of files** which can be texts, images, songs... The aim is to **avoid losing** documents.

Run SafeMyWork and select your working folders. Then while you are working, every a certain amount of time, all files in this folder will be copied into a separate folder. It keeps your files safe if you forget to save your work or delete accidentally files.

It can also synchronize two folders.

## Current state

### Version
The current version is 0.5.

### Features
 - watch different directories
 - specify directories, files, and extensions to exclude
 - interface (gtk)
 - automatic saving tab
 - synchronization tab
  - conflicts file resolution
  - confirm dialog
 - safe mode:
  - 3 Go maximum  folder size to copy
  - 250 maximum shown conflicts in conflicts dialog

### TODO
 - **files in confirm dialog in a ListView widget with toggle buttons**
 - **Conflict dialog: be able to keep the two files**
 - Add unit tests
 - dialog for errors (sync)
 - show the size to estimate how long will it take
 - show the size of safe_doc
 - 3 Go limit in settings
 - PEP 471: use of os.scandir instead of walk

#### Other concepts
 - make an history of each files
 - compress files
 - add little icon to symbolize file explorer in open folder buttons

## Launch the app
Run `python3 main.py`.

## Documentation
You will need to have [Sphinx](http://sphinx-doc.org/) installed.
Then run `python3 -m pip install sphinx_rtd_theme` for the ReadTheDocs theme.
To build the doc:

	git clone git@github.com:Thykof/SafeMyWork.git
	cd SafeMyWork
	cd docs
	build html

The documentation is in `docs/_build/html/index.html`.

## License
SafeMyWork is under the GNU GPL v3 license.

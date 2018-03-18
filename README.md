# Safe My work
SafeMyWork save all files in the given directory into another directory to keep your work safe and avoid loosing data and time.

[![Documentation Status](https://readthedocs.org/projects/safemywork/badge/?version=develop)](http://safemywork.readthedocs.io/en/develop/?badge=develop)
[![Build Status](https://travis-ci.org/Thykof/SafeMyWork.svg?branch=master)](https://travis-ci.org/Thykof/SafeMyWork)
[![Code Health](https://landscape.io/github/Thykof/SafeMyWork/master/landscape.svg?style=flat)](https://landscape.io/github/Thykof/SafeMyWork/master)

## What for ?
SafeMyWork is intend for people who handle lot of files which can be texts, images, songs.

Run SafeMyWork and give it a directory to working directory. Then while you are working, every ten minutes all files in this directory will be copy in another directory. As the result of keeping them safe if you does not save your work or delete accidentally files.

## Version
Current version is 0.4
#### Current state
 - watch different directories
 - specify directories, files and extensions to exclude
 - interface (gtk)
 - safe mode:
  - 3 Go copy max
  - 250 conflicts max show

Work in progress...

#### TODO
 - **files in confirm dialog in a ListView widget with toggle buttons**
 - **Conflict dialog: be able to keep the two files***
 - dialog for errors (sync)
 - show the size to estimate how long will it take
 - show the size of safe_doc
 - 3 Go limit in settings
 - PEP 471 : use of os.scandir instead of walk
 - make an history of each files
 - compress files
 - add little icon to symbolize file explorer in open folder buttons


## Launch the app
Run `python3 main.py`.

## Documenation
How to build the doc:

	git clone git@github.com:Thykof/SafeMyWork.git
	cd SafeMyWork
	cd docs
	build html

The documentation is in `docs/_build/html/index.html`.

## License
SafeMyWork is under the GNU GPL v3 license.

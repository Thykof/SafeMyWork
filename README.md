# Safe My work
SafeMyWork saves all files in the given directory into another directory to keep your work safe and avoid losing data and time.

[![Documentation Status](https://readthedocs.org/projects/safemywork/badge/?version=master)](http://safemywork.readthedocs.io/en/master/?badge=master)
[![Build Status](https://travis-ci.org/Thykof/SafeMyWork.svg?branch=master)](https://travis-ci.org/Thykof/SafeMyWork)

## What for?
SafeMyWork is intended for people who **handle a lot of files** which can be texts, images, songs... The aim is to **avoid losing** documents.

### GUI (Linux)

Run SafeMyWork and select your working folders. Then while you are working, every a certain amount of time, all files in this folder will be copied into a separate folder. It keeps your files safe if you forget to save your work or delete accidentally files.

It can also synchronize two folders.

### CLI (Linux & Windows)

*Command line interface*

Download the latest release here: <https://github.com/Thykof/SafeMyWork/releases>. Unzip.

#### Windows

Open a terminal window (`cmd.exe`) and type `cli.exe --help` to see how to use the command line interface.


#### Linux (Ubuntu)

Open a terminal window and type `cli --help` to see how to use the command line interface.

### Example

The command...

    cli -w /home/username/work-folder --extentions txt,pdf -t filter -d 5 --dirname .git -n 2 --dirpath build/classes

...will copie all files in `/home/username/work-folder` except the files ending with `txt` and `pdf`
and except the folders named `.git` and except the folder `build/classes` every 5 minutes and it will do this 2 times.

## Current state

### Version
The current version is 0.6.2.

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

## Generate the documentation
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

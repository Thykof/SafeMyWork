# Safe My work
SafeMyWork save all files in the given directory in another directory to keep your work safe and avoid loosing data.

[![Documentation Status](https://readthedocs.org/projects/safemywork/badge/?version=develop)](http://safemywork.readthedocs.org/en/develop)
[![Build Status](https://travis-ci.org/Thykof/SafeMyWork.svg?branch=develop)](https://travis-ci.org/Thykof/SafeMyWork)
[![Code Health](https://landscape.io/github/Thykof/SafeMyWork/develop/landscape.svg?style=flat)](https://landscape.io/github/Thykof/SafeMyWork/develop)

## Version
Current version is 1.0
#### Current state
 - feature/outline
 - watch different directories
 - specify directories, files and extensions to exclude
 - interface (gtk)
 - safe mode:
  - 3 Go copy max
  - 250 conflicts max show

Work in progress...

#### TODO
 - **files in confirm dialog in a ListView widget with toggle buttons**
 - show the size to estimate how long will it take
 - show the size of safe_doc
 - 3 Go limit in settings
 - PEP 471 : use of os.scandir instead of walk
 - make an history of each files
 - compress files
 - add little icon to symbolize file explorer in open folder buttons

## What for ?
SafeMyWork is intend for people who handle lot of files which can be texts, images, songs.

Run SafeMyWork and give it a directory to watch. Then while you are working, every ten minutes all files in this directory will be copy in another directory. As the result of keeping them safe if you does not save your work or delete accidentally files.

## License
SafeMyWork is under the GNU GPL v3 license.

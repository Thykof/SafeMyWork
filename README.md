# Safe My work
SafeMyWork save all files in the given directory in another directory to keep your work safe and avoid losing data.

[![Documentation Status](https://readthedocs.org/projects/safemywork/badge/?version=develop)](http://safemywork.readthedocs.org/en/develop)
[![Build Status](https://travis-ci.org/Thykof/SafeMyWork.svg?branch=win)](https://travis-ci.org/Thykof/SafeMyWork)
[![Code Health](https://landscape.io/github/Thykof/SafeMyWork/win/landscape.svg?style=flat)](https://landscape.io/github/Thykof/SafeMyWork/win)

## Version
Current version is 0.2.
#### Current state
 - feature/outline
 - watch different directories
 - specify files and extensions to exclude

Work in progress...

#### TODO
 - make an history of each files
 - compress files
 - interface (gtk)

## What for ?
SafeMyWork is intend for people who handle lot of files which can be texts, images, songs.

Run SafeMyWork and give it a directory to watch. Then while you are working, every ten minutes all files in this directory will be copy in another directory. As the result of keeping them safe if you does not save your work or delete accidentally files.

## How to use it ?
Run `python3 main.py <path-to-your-dir>` to start. The given path is the directory watching. You don't need extra requirement.

## License
SafeMyWork is under the GNU GPL v3 license.

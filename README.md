# Duplicates

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/link-duplicates)
![PyPI - Version](https://img.shields.io/pypi/v/link-duplicates)
![Tests](https://github.com/MusicalNinjaRandInt/duplicates/actions/workflows/CI.yaml/badge.svg?branch=main)
[![codecov](https://codecov.io/gh/MusicalNinjaRandInt/duplicates/graph/badge.svg?token=WGZ7PR5IXC)](https://codecov.io/gh/MusicalNinjaRandInt/duplicates)

Identify duplicate files and replace them with hardlinks on any OS.

Intended to be used to reduce the storage space taken up by mutliple copies of similar backups. (E.g. regular google takeouts)

## Usage

Can be run from a command line in Linux, MacOS or Windows and will recursively scan a directory, identify and optionally hardlink any duplicate files found.

**WARNING:** Hardlinking files means if you change any one "copy" all "copies" will change.

**WARNING:** If other hardlinks are present _outside_ the directories scanned, these may no longer point to the same inode as those within the scanned directories. Consider the situation as _undefined_.

### Command line

`dupes PATH` will display number of duplicate files found under `PATH`

`dupes PATH1 PATH2 ...` will display number of duplicate files found under _and across_ `PATH1` and `PATH2`

`dupes --list PATHS...` will list the full sets of duplicate files found

`dupes --short PATHS...` will only list sets of duplicates where there are different file names

and finally ...

`dupes --link PATHS...` will replace duplicate files with hard links

### Python

You can also use the class `DuplicateFiles` to indentify and optionally link duplicates.

Additionally `BufferedIOFile` provides a binary file which knows its `Path` and offers a `readchunk()` method similar to the text file `readline()`.

## Up Next

- [Keep original file mode after hardlinking](https://github.com/MusicalNinjaRandInt/duplicates/issues/13)
- [Select leading inode for linking](https://github.com/MusicalNinjaRandInt/duplicates/issues/14)
- [Improved exception handling from the command line](https://github.com/MusicalNinjaRandInt/duplicates/issues/15)

Please vote on any issues which are important to you.

![PyPI - Downloads](https://img.shields.io/pypi/dm/link-duplicates)

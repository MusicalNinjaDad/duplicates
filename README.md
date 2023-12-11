# Duplicates

Identify duplicate files and replace them with hardlinks on any OS.

Intended to be used to reduce the storage space taken up by mutliple copies of similar backups. (E.g. regular google takeouts)

## Usage

Can be run from a command line in Linux, MacOS or Windows and will recursively scan a directory, identify and optionally hardlink any duplicate files found.

WARNING: Hardlinking files means if you change any one "copy" all "copies" will change.

### Command line

`dupes PATH` will display number of duplicate files found under PATH

`dupes --list PATH` will list the full sets of duplicate files found

`dupes --short PATH` will only list sets of duplicates where there are different file names

and finally ...

`dupes --link PATH` will replace duplicate files with hard links

### Python

You can also use the class `DuplicateFiles` to indentify and optionally link duplicates.

Additionally `BufferedIOFile` provides a binary file which knows its `Path` and offers a `readchunk()` method similar to the text file `readline()`.

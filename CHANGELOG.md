# CHANGELOG - Link Duplicates

- `BufferedIOFile()` expects all arguments _except `path`_ as keyword arguments

## 0.4.0 - multiple paths

- allow multiple paths to be passed at command line
- allow multiple paths to be passed to `DuplicateFiles.frompath()` and therefore rename it to `DuplicateFiles.frompaths()`
- check that all paths are on same filesystem, otherwise hard linking is not possible

## 0.3.0 - speed improvements

- speed up cases where reprocessing after a previous run
- add totals to info output

## v0.2.3

- add timestamps to status output

## v0.2.2

- send status output to stderr to allow `--list` to be redirected to a file

## v0.2.1

- improved output while running to give some kind of info on progress

## v0.2.0 - improved output

- added info on storage usage and savings
- added confirmation prompt and -y option for linking

## v0.1.6 - improved handling of files to ignore

- ignore symlinks
- ignore files of zero size completely

## v0.1.5

- avoid crashing out with a `StopIteration` when path contains multiple files with zero size

## v0.1.4

- avoid `ValueError` when path contains files with zero size

## v0.1.3

- reworked file comparison to avoid overrunning maximum recursion depth

## v0.1.2

- fix `--list` and `--short`

## v0.1.1

- Initial Version

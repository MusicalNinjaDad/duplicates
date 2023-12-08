from itertools import permutations

from recurtools import flatten
from . import *

SEPARATOR = '\n=====================\n'

# @mark.skip
@mark.copyfiles(('fileA',2), ('fileA2',2), ('fileB',3))
def test_printoutcontents(copiedtestfiles):
    files = [
        'fileA',
        'fileA2',
        'fileB'
    ]

    filepaths = [str(path) for file in files for path in copiedtestfiles.paths[file]]

    dupes = {frozenset(BufferedIOFile(path) for path in filepaths) for filepaths in copiedtestfiles.paths.values()}
    duplicatefiles = DuplicateFiles(duplicates=dupes, inoindex=None)
    returnedstring = duplicatefiles.printout()

    stringblocks = returnedstring.split(SEPARATOR)
    assert len(stringblocks) == 3
    
    stringelements = [s.split('\n') for s in stringblocks]
    assert all([path in flatten(stringelements, preservestrings=True) for path in filepaths])

    fileApaths = permutations([str(path) for path in copiedtestfiles.paths['fileA']])
    assert any([list(permutation) in stringelements for permutation in fileApaths])

    fileBpaths = permutations([str(path) for path in copiedtestfiles.paths['fileB']])
    assert any([list(permutation) in stringelements for permutation in fileBpaths])

    fileA2paths = permutations([str(path) for path in copiedtestfiles.paths['fileB']])
    assert any([list(permutation) in stringelements for permutation in fileA2paths])
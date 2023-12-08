from itertools import permutations

from pytest import fixture

from recurtools import flatten
from . import *

SEPARATOR = '\n=====================\n'
#separator is part of commited interface as others may choose to parse this output

@mark.copyfiles(('fileA',2), ('fileA2',2), ('fileB',3))
class TestPrintoutcontents:
    files = [
            'fileA',
            'fileA2',
            'fileB'
        ]

    @fixture(scope='class', autouse=True)
    def setup(self, request, classtestfiles):
        files = request.cls.files
        request.cls.filepaths = [str(path) for file in files for path in classtestfiles.paths[file]]

        dupes = {frozenset(BufferedIOFile(path) for path in filepaths) for filepaths in classtestfiles.paths.values()}
        duplicatefiles = DuplicateFiles(duplicates=dupes, inoindex=None)
        returnedstring = duplicatefiles.printout()

        request.cls.stringblocks = returnedstring.split(SEPARATOR)
        request.cls.stringelements = [s.split('\n') for s in self.stringblocks]

    def test_correctnumberofblocks(self):
        assert len(self.stringblocks) == 3
    
    def test_correctpaths(self):  
        assert all([path in flatten(self.stringelements, preservestrings=True) for path in self.filepaths]), 'Some paths missing in output'
        assert all([path in self.filepaths for path in flatten(self.stringelements, preservestrings=True)]), 'Additional paths found in output'

    @mark.parametrize('fileid', files)
    def test_pathsgrouped(self, fileid, classtestfiles):
        filepaths = [list(p) for p in permutations([str(path) for path in classtestfiles.paths[fileid]])]
        assert any([permutation in self.stringelements for permutation in filepaths]), f'{fileid} paths not properly grouped'
    
    @mark.parametrize('fileid', files)
    def test_pathgroupexists(self, fileid, classtestfiles):
        filepaths = [list(p) for p in permutations([str(path) for path in classtestfiles.paths[fileid]])]
        assert any([groupofpaths in filepaths for groupofpaths in self.stringelements]), f'{fileid} path group not found'

@mark.copyfiles(('fileA',2), ('fileA2',2), ('fileB',3), ('fileA-copy',1))
def test_printoutcontents_frompath(copiedtestfiles):
    files = [
        'fileA',
        'fileA2',
        'fileA-copy',
        'fileB'
    ]

    filepaths = [str(path) for file in files for path in copiedtestfiles.paths[file]]

    duplicatefiles = DuplicateFiles.frompath(copiedtestfiles.root)
    returnedstring = duplicatefiles.printout()

    stringblocks = returnedstring.split(SEPARATOR)
    assert len(stringblocks) == 3
    
    stringelements = [s.split('\n') for s in stringblocks]
    assert all([path in flatten(stringelements, preservestrings=True) for path in filepaths]), 'Some paths missing in output'
    assert all([path in filepaths for path in flatten(stringelements, preservestrings=True)]), 'Additional paths found in output'

    fileApaths = [list(p) for p in permutations([str(path) for path in copiedtestfiles.paths['fileA'] + copiedtestfiles.paths['fileA-copy']])]
    assert any([permutation in stringelements for permutation in fileApaths]), 'fileA paths not properly grouped'
    assert any([groupofpaths in fileApaths for groupofpaths in stringelements]), 'fileA path group not found'

    fileBpaths = [list(p) for p in permutations([str(path) for path in copiedtestfiles.paths['fileB']])]
    assert any([permutation in stringelements for permutation in fileBpaths]),  'fileB paths not properly grouped'
    assert any([groupofpaths in fileBpaths for groupofpaths in stringelements]), 'fileB path group not found'

    fileA2paths = [list(p) for p in permutations([str(path) for path in copiedtestfiles.paths['fileA2']])]
    assert any([permutation in stringelements for permutation in fileA2paths]), 'fileA2 paths not properly grouped'
    assert any([groupofpaths in fileA2paths for groupofpaths in stringelements]), 'fileA2 path group not found'

@mark.copyfiles(('fileA',2), ('fileA2',2), ('fileB',3), ('fileA-copy',1))
def test_printoutcontents_ignoresamenames(copiedtestfiles):
    files = [
        'fileA',
        'fileA-copy'
    ]

    filepaths = [str(path) for file in files for path in copiedtestfiles.paths[file]]

    duplicatefiles = DuplicateFiles.frompath(copiedtestfiles.root)
    returnedstring = duplicatefiles.printout(ignoresamenames=True)

    stringblocks = returnedstring.split(SEPARATOR)
    assert len(stringblocks) == 1
    
    stringelements = [s.split('\n') for s in stringblocks]
    assert all([path in flatten(stringelements, preservestrings=True) for path in filepaths]), f'Some paths missing in output: {stringelements}'
    assert all([path in filepaths for path in flatten(stringelements, preservestrings=True)]), f'Additional paths found in output: {stringelements}'

    fileApaths = [list(p) for p in permutations([str(path) for path in copiedtestfiles.paths['fileA'] + copiedtestfiles.paths['fileA-copy']])]
    assert any([permutation in stringelements for permutation in fileApaths]), f'fileA paths not properly grouped: {stringelements}'
    assert any([groupofpaths in fileApaths for groupofpaths in stringelements]), f'fileA path group not found: {stringelements}'
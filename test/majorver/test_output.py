from itertools import permutations

from pytest import fixture

from recurtools import flatten
from . import *

SEPARATOR = '\n=====================\n'
#separator is part of commited interface as others may choose to parse this output

@fixture(scope='class', autouse=True)
def setup(request, classtestfiles):
    testclass = request.cls
    files = flatten(testclass.filegroups.values(), preservestrings=True)
    testclass.filepaths = [str(path) for file in files for path in classtestfiles.paths[file]]

    returnedstring = testclass.act(classtestfiles)

    testclass.stringblocks = returnedstring.split(SEPARATOR)
    testclass.stringelements = [s.split('\n') for s in testclass.stringblocks]

@mark.copyfiles(('fileA',2), ('fileA2',2), ('fileB',3))
class TestPrintoutcontents:
    filegroups = {
            'fileA': ('fileA',),
            'fileA2': ('fileA2',),
            'fileB': ('fileB',)
    }

    def act(testfiles):
        dupes = {frozenset(BufferedIOFile(path) for path in filepaths) for filepaths in testfiles.paths.values()}
        duplicatefiles = DuplicateFiles(duplicates=dupes, inoindex=None)
        return duplicatefiles.printout()

    def test_correctnumberofblocks(self):
        assert len(self.stringblocks) == len(self.filegroups)
    
    def test_correctpaths(self):  
        assert all([path in flatten(self.stringelements, preservestrings=True) for path in self.filepaths]), f'Some paths missing in output. Expected {self.filepaths}, got: {flatten(self.stringelements, preservestrings=True)}'
        assert all([path in self.filepaths for path in flatten(self.stringelements, preservestrings=True)]), f'Additional paths found in output. Expected {self.filepaths}, got: {flatten(self.stringelements, preservestrings=True)}'

    @mark.parametrize('filegroup', filegroups.values(), ids=filegroups)
    def test_pathsgrouped(self, filegroup, classtestfiles):
        groupedpaths = [p for fileid in filegroup for p in classtestfiles.paths[fileid]]
        filepaths = [list(permutation) for permutation in permutations([str(path) for path in groupedpaths])]
        assert any([permutation in self.stringelements for permutation in filepaths]), f'{filegroup} paths not properly grouped. Expected: {groupedpaths}, got: {self.stringelements}'

    @mark.parametrize('filegroup', filegroups.values(), ids=filegroups)
    def test_pathgroupexists(self, filegroup, classtestfiles):
        groupedpaths = [p for fileid in filegroup for p in classtestfiles.paths[fileid]]
        filepaths = [list(permutation) for permutation in permutations([str(path) for path in groupedpaths])]
        assert any([groupofpaths in filepaths for groupofpaths in self.stringelements]), f'{filegroup} path group not found. Expected: {groupedpaths}, got: {self.stringelements}'

@mark.copyfiles(('fileA',2), ('fileA2',2), ('fileB',3), ('fileA-copy',1))
class TestPrintoutcontents_frompath:
    filegroups = {
        'fileA': ('fileA','fileA-copy'),
        'fileA2': ('fileA2',),
        'fileB': ('fileB',)
    }
    
    def act(testfiles):
        duplicatefiles = DuplicateFiles.frompaths(testfiles.root)
        return duplicatefiles.printout()
    def test_correctnumberofblocks(self):
        assert len(self.stringblocks) == len(self.filegroups)
    
    def test_correctpaths(self):  
        assert all([path in flatten(self.stringelements, preservestrings=True) for path in self.filepaths]), f'Some paths missing in output. Expected {self.filepaths}, got: {flatten(self.stringelements, preservestrings=True)}'
        assert all([path in self.filepaths for path in flatten(self.stringelements, preservestrings=True)]), f'Additional paths found in output. Expected {self.filepaths}, got: {flatten(self.stringelements, preservestrings=True)}'

    @mark.parametrize('filegroup', filegroups.values(), ids=filegroups)
    def test_pathsgrouped(self, filegroup, classtestfiles):
        groupedpaths = [p for fileid in filegroup for p in classtestfiles.paths[fileid]]
        filepaths = [list(permutation) for permutation in permutations([str(path) for path in groupedpaths])]
        assert any([permutation in self.stringelements for permutation in filepaths]), f'{filegroup} paths not properly grouped. Expected: {groupedpaths}, got: {self.stringelements}'

    @mark.parametrize('filegroup', filegroups.values(), ids=filegroups)
    def test_pathgroupexists(self, filegroup, classtestfiles):
        groupedpaths = [p for fileid in filegroup for p in classtestfiles.paths[fileid]]
        filepaths = [list(permutation) for permutation in permutations([str(path) for path in groupedpaths])]
        assert any([groupofpaths in filepaths for groupofpaths in self.stringelements]), f'{filegroup} path group not found. Expected: {groupedpaths}, got: {self.stringelements}'

@mark.copyfiles(('fileA',2), ('fileA2',2), ('fileB',3), ('fileA-copy',1))
class TestPrintoutcontents_Ignoresamenames():
    filegroups = {
        'fileA': ('fileA','fileA-copy')
    }

    def act(testfiles):
        duplicatefiles = DuplicateFiles.frompaths(testfiles.root)
        return duplicatefiles.printout(ignoresamenames=True)

    def test_correctnumberofblocks(self):
        assert len(self.stringblocks) == len(self.filegroups)
    
    def test_correctpaths(self):  
        assert all([path in flatten(self.stringelements, preservestrings=True) for path in self.filepaths]), f'Some paths missing in output. Expected {self.filepaths}, got: {flatten(self.stringelements, preservestrings=True)}'
        assert all([path in self.filepaths for path in flatten(self.stringelements, preservestrings=True)]), f'Additional paths found in output. Expected {self.filepaths}, got: {flatten(self.stringelements, preservestrings=True)}'

    @mark.parametrize('filegroup', filegroups.values(), ids=filegroups)
    def test_pathsgrouped(self, filegroup, classtestfiles):
        groupedpaths = [p for fileid in filegroup for p in classtestfiles.paths[fileid]]
        filepaths = [list(permutation) for permutation in permutations([str(path) for path in groupedpaths])]
        assert any([permutation in self.stringelements for permutation in filepaths]), f'{filegroup} paths not properly grouped. Expected: {groupedpaths}, got: {self.stringelements}'

    @mark.parametrize('filegroup', filegroups.values(), ids=filegroups)
    def test_pathgroupexists(self, filegroup, classtestfiles):
        groupedpaths = [p for fileid in filegroup for p in classtestfiles.paths[fileid]]
        filepaths = [list(permutation) for permutation in permutations([str(path) for path in groupedpaths])]
        assert any([groupofpaths in filepaths for groupofpaths in self.stringelements]), f'{filegroup} path group not found. Expected: {groupedpaths}, got: {self.stringelements}'
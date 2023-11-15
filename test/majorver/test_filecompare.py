from pytest import fixture
from . import listfiles, finddupes, Path, duplicatedir1, testfiles

def test_fileisduplicate(duplicatedir1):
    testfiles = duplicatedir1
    filesdict = listfiles(testfiles)
    duplicatefiles = finddupes(filesdict)
    assert duplicatefiles == {frozenset((testfiles / 'dir1' / 'FileA.txt', testfiles / 'alt' / 'dir1' / 'FileA.txt'))}
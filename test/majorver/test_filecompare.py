from pytest import mark
from . import listfiles, filesofsamesize, Path, duplicatedir1, testfiles, BufferedIOFile, comparefiles

def test_fileissamesize(duplicatedir1):
    testfiles = duplicatedir1
    filesdict = listfiles(testfiles)
    duplicatefiles = filesofsamesize(filesdict)
    assert duplicatefiles == {frozenset((testfiles / 'dir1' / 'fileA.txt', testfiles / 'alt' / 'dir1' / 'fileA.txt'))}

@mark.xfail
def test_samefilecontents(duplicatedir1):
    testfiles = duplicatedir1
    filestocompare = {frozenset(map(BufferedIOFile,(testfiles / 'dir1' / 'fileA.txt', testfiles / 'alt' / 'dir1' / 'fileA.txt')))}
    identicalfiles = comparefiles(filestocompare)
    assert identicalfiles == filestocompare
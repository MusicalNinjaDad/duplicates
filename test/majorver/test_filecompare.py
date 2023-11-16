from . import listfiles, filesofsamesize, Path, duplicatedir1, testfiles

def test_fileissamesize(duplicatedir1):
    testfiles = duplicatedir1
    filesdict = listfiles(testfiles)
    duplicatefiles = filesofsamesize(filesdict)
    assert duplicatefiles == {frozenset((testfiles / 'dir1' / 'fileA.txt', testfiles / 'alt' / 'dir1' / 'fileA.txt'))}

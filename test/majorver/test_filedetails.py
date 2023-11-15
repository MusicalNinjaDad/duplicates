from pytest import fixture
from recurtools import flatten

from . import Path, listfiles

dir1 = Path('test/majorver/data/dir1')
dir2 = Path('test/majorver/data/dir2')

@fixture
def testfiles(tmp_path):
    dir1.copy(tmp_path)
    dir2.copy(tmp_path)
    return tmp_path    

def test_fileslisted(testfiles):
    filesdict = listfiles(testfiles)
    files = [file for file in flatten(filesdict.values())]
    assert len(files) == 2
    assert Path(testfiles / 'dir1' / 'fileA.txt') in files
    assert Path(testfiles / 'dir2' / 'fileB.txt') in files

def test_filesindexedbysize(testfiles):
    filesdict = listfiles(testfiles)
    assert filesdict == {
        16: [Path(testfiles / 'dir1' / 'fileA.txt')],
        23: [Path(testfiles / 'dir2' / 'fileB.txt')]
    }
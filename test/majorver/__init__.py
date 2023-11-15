from pytest import fixture
from .. import *
from pathlib import Path

dir1 = Path('test/majorver/data/dir1')
dir2 = Path('test/majorver/data/dir2')

@fixture
def testfiles(tmp_path) -> Path:
    dir1.copy(tmp_path)
    dir2.copy(tmp_path)
    return tmp_path

@fixture
def duplicatedir1(testfiles) -> Path:
    tmp_path = testfiles
    dir1.copy(testfiles / 'alt')
    return tmp_path    

def _copy(self: Path, target: Path) -> None:
    from shutil import copytree
    if self.is_dir():
        copytree(self, target / self.name)
    else:
        raise NotImplementedError

Path.copy = _copy
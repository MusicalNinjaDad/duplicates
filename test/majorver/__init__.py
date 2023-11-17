from pytest import fixture
from .. import *
from pathlib import Path

dir1 = Path('test/majorver/data/dir1')
dir2 = Path('test/majorver/data/dir2')

def _copy(self: Path, target: Path) -> None:
    from shutil import copytree
    if self.is_dir():
        copytree(self, target / self.name)
    else:
        raise NotImplementedError

Path.copy = _copy
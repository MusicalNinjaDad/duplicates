from collections import namedtuple
from dataclasses import dataclass
from io import BufferedIOBase
from pathlib import Path
from pytest import fixture, mark, raises

def _copy(self: Path, target: Path) -> None:
    from shutil import copytree
    if self.is_dir():
        copytree(self, target / self.name)
    else:
        raise NotImplementedError

Path.copy = _copy

dir1 = Path('test/majorver/data/dir1')
dir2 = Path('test/majorver/data/dir2')

@dataclass
class testfiles():
    root: Path
    paths: dict[str: Path]
    handles: dict[str: BufferedIOBase]

def openfileandreturntuple(filepath):
    with filepath.open('rb') as filehandle:
        yield(namedtuple('testfile', ['path', 'handle'])(filepath, filehandle))

@fixture
def copiedtestfiles(tmp_path) -> testfiles:
    dir1.copy(tmp_path)
    dir2.copy(tmp_path)
    tmp_files = testfiles(
        root = tmp_path,
        paths = {
            'dir1': Path(tmp_path / 'dir1'),
            'dir2': Path(tmp_path / 'dir2'),
            'fileA': Path(tmp_path / 'dir1' / 'fileA.txt'),
            'fileB': Path(tmp_path / 'dir2' / 'fileB.txt')
        },
        handles = {}
    )
    return tmp_files

@fixture
def duplicatedir1(copiedtestfiles) -> Path:
    dir1.copy(copiedtestfiles.root / 'alt')
    copiedtestfiles.paths['dir1-copy'] = copiedtestfiles.root / 'alt' 
    copiedtestfiles.paths['fileA-copy'] = copiedtestfiles.root / 'alt' / 'dir1' / 'fileA.txt'
    return copiedtestfiles

@fixture
def fileAopened(tmp_path):
    dir1.copy(tmp_path)
    tmp_files = testfiles(
        root = tmp_path,
        paths = {
            'dir1': Path(tmp_path / 'dir1'),
            'fileA': Path(tmp_path / 'dir1' / 'fileA.txt'),
        },
        handles = {}
    )
    with tmp_files.paths['fileA'].open('rb') as filehandle:
        tmp_files.handles['fileA'] = filehandle
        yield tmp_files

@fixture
def fileBopened(tmp_path):
    dir2.copy(tmp_path)
    tmp_files = testfiles(
        root = tmp_path,
        paths = {
            'dir1': Path(tmp_path / 'dir2'),
            'fileB': Path(tmp_path / 'dir2' / 'fileB.txt'),
        },
        handles = {}
    )
    with tmp_files.paths['fileB'].open('rb') as filehandle:
        tmp_files.handles['fileB'] = filehandle
        yield tmp_files
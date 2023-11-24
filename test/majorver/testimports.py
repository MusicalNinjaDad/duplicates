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
class Testfiles():
    root: Path
    paths: dict[str: Path]
    handles: dict[str: BufferedIOBase]

@fixture
def copiedtestfiles(tmp_path) -> Testfiles:
    dir1.copy(tmp_path)
    dir2.copy(tmp_path)
    tmp_files = Testfiles(
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
def duplicatedir1(copiedtestfiles) -> Testfiles:
    dir1.copy(copiedtestfiles.root / 'alt')
    copiedtestfiles.paths['dir1-copy'] = copiedtestfiles.root / 'alt' 
    copiedtestfiles.paths['fileA-copy'] = copiedtestfiles.root / 'alt' / 'dir1' / 'fileA.txt'
    return copiedtestfiles

@fixture
def twocopiesfileAopen(duplicatedir1) -> Testfiles:
    with duplicatedir1.paths['fileA'].open('rb') as handle1, duplicatedir1.paths['fileA-copy'].open('rb') as handle2:
        duplicatedir1.handles['fileA'] = handle1
        duplicatedir1.handles['fileA-copy'] = handle2
        yield duplicatedir1

@fixture
def fileAopened(copiedtestfiles):
    with copiedtestfiles.paths['fileA'].open('rb') as filehandle:
        copiedtestfiles.handles['fileA'] = filehandle
        yield

@fixture
def fileBopened(copiedtestfiles):
    with copiedtestfiles.paths['fileB'].open('rb') as filehandle:
        copiedtestfiles.handles['fileB'] = filehandle
        yield

@fixture
def fileAcopyopened(copiedtestfiles):
    with copiedtestfiles.paths['fileA-copy'].open('rb') as filehandle:
        copiedtestfiles.handles['fileA-copy'] = filehandle
        yield
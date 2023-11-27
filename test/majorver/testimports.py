from collections import defaultdict
from contextlib import ExitStack
from dataclasses import dataclass
from io import BufferedIOBase
from pathlib import Path
import uuid
from pytest import fixture, mark, raises

def _copy(self: Path, target: Path) -> None:
    from shutil import copytree, copyfile
    if self.is_dir():
        copytree(self, target / self.name)
    else:
        copyfile(self, target / self.name) #If later needed can use newname = self.name: str as optional arg

Path.copy = _copy

dir1 = Path('test/majorver/data/dir1')
dir2 = Path('test/majorver/data/dir2')

@dataclass
class Testfiles():
    root: Path
    paths: dict[str: Path]
    handles: dict[str: BufferedIOBase]

SourceFileRoot = Path('test/majorver/data/')
sourcefiles = Testfiles(
    root = SourceFileRoot,
    paths = {
        'fileA': SourceFileRoot / 'dir1' / 'fileA.txt',
        'fileB': SourceFileRoot / 'dir2' / 'fileB.txt'
    },
    handles = {}
)

@fixture
def copiedtestfiles(request, tmp_path) -> Testfiles:
    tmp_files = Testfiles(
        root = tmp_path,
        paths = defaultdict(list),
        handles = defaultdict(list)
    )

    filestocopy = request.node.get_closest_marker('copyfiles')
    for file in filestocopy.args:
        fileid, numcopies = file
        for i in range(numcopies):
            uniquedir = tmp_path / str(uuid.uuid1())
            uniquedir.mkdir()
            sourcefiles.paths[fileid].copy(tmp_path / uniquedir)
            tmp_files.paths[fileid].append(tmp_path / uniquedir / sourcefiles.paths[fileid].name)
    filestolink = request.node.get_closest_marker('linkfiles')
    if filestolink:
        for file in filestolink.args:
            fileid, numcopies = file
            for i in range(numcopies):
                uniquedir = tmp_path / str(uuid.uuid1())
                uniquedir.mkdir()
                newfile = tmp_path / uniquedir / sourcefiles.paths[fileid].name
                newfile.hardlink_to(tmp_files.paths[fileid][0])
                tmp_files.paths[fileid].append(newfile)
    yield tmp_files

@fixture
def filesopen(copiedtestfiles):
    with ExitStack() as stack:
        copiedtestfiles.handles = {
            fileid: [stack.enter_context(open(path, 'rb')) for path in paths]
            for fileid, paths in copiedtestfiles.paths.items()
        }
        yield

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

@fixture
def fileAhardlinked(copiedtestfiles):
    copiedtestfiles.paths['fileA-link'] = copiedtestfiles.root / 'fileAlink.txt'
    copiedtestfiles.paths['fileA-link'].hardlink_to(copiedtestfiles.paths['fileA'])
    return copiedtestfiles

@fixture
def fileAlinkopened(copiedtestfiles):
    with copiedtestfiles.paths['fileA-link'].open('rb') as filehandle:
        copiedtestfiles.handles['fileA-link'] = filehandle
        yield

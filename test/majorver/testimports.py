import uuid
from collections import defaultdict
from contextlib import ExitStack
from dataclasses import dataclass
from io import BufferedIOBase
from pathlib import Path

from pytest import fixture, mark, raises


def _copy(self: Path, target: Path) -> None:
    from shutil import copyfile, copytree
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
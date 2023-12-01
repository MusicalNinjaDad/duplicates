import uuid
from collections import defaultdict
from contextlib import ExitStack
from dataclasses import dataclass
from io import BufferedIOBase
from pathlib import Path

from pytest import fixture

def pytest_configure(config):
    marks = [
        "copyfiles((file, num),(file, num),...): which files to copy",
        "linkfiles((file, num),(file, num),...): which files to hardlink"
    ]

    def addmarkers(marks):
        for mark in marks:
            config.addinivalue_line("markers", mark)

    addmarkers(marks)

def _copy(self: Path, target: Path) -> None:
    from shutil import copyfile, copytree
    if self.is_dir():
        copytree(self, target / self.name)
    else:
        copyfile(self, target / self.name) #If later needed can use newname = self.name: str as optional arg

def _copyfrom(self: Path, source: Path) -> None:
    from shutil import copyfile
    copyfile(source, self)

Path.copy = _copy
Path.copyfrom = _copyfrom

@dataclass
class Testfiles():
    root: Path
    paths: dict[str: Path]
    handles: dict[str: BufferedIOBase]

SourceFileRoot = Path('test/data/')
sourcefiles = Testfiles(
    root = SourceFileRoot,
    paths = {
        'fileA': SourceFileRoot / 'dir1' / 'fileA.txt',
        'fileB': SourceFileRoot / 'dir2' / 'fileB.txt',
        'fileA2': SourceFileRoot / 'dir3' / 'fileA2.txt',
        'fileB2': SourceFileRoot / 'dir3' / 'fileB2.txt'
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
        for _ in range(numcopies):
            uniquedir = tmp_path / str(uuid.uuid1())
            uniquedir.mkdir()
            newfile = tmp_path / uniquedir / sourcefiles.paths[fileid].name
            newfile.copyfrom(sourcefiles.paths[fileid])
            tmp_files.paths[fileid].append(newfile)
    filestolink = request.node.get_closest_marker('linkfiles')
    if filestolink:
        for file in filestolink.args:
            fileid, numcopies = file
            for _ in range(numcopies):
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
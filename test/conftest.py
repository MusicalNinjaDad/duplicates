import uuid
from collections import defaultdict
from contextlib import ExitStack
from dataclasses import dataclass
from io import BufferedIOBase
from pathlib import Path
from shutil import copyfile

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
        'fileB2': SourceFileRoot / 'dir3' / 'fileB2.txt',
        'fileA-copy': SourceFileRoot / 'dir3' / 'fileA-copy.txt'
    },
    handles = {}
)

@fixture
def copiedtestfiles(request, tmp_path) -> Testfiles:
    filestocopy = request.node.get_closest_marker('copyfiles')
    if filestocopy.args:
        yield copytestfiles(request, tmp_path, filestocopy.args)
    else:
        def mktmp(id): 
            dir = tmp_path / Path(id)
            dir.mkdir()
            return dir
        yield {setname: copytestfiles(request, mktmp(setname), setoffiles) for setname, setoffiles in filestocopy.kwargs.items()}
        

@fixture(scope='class')
def classtestfiles(request, tmp_path_factory) -> Testfiles:
    tmp_dir = tmp_path_factory.mktemp(str(request.node.name))
    filestocopy = request.node.get_closest_marker('copyfiles')
    if filestocopy.args:
        yield copytestfiles(request, tmp_dir, filestocopy.args)
    else:
        raise NotImplementedError

def copytestfiles(request, tmp_path, filestocopy) -> Testfiles:
    tmp_files = Testfiles(
        root = tmp_path,
        paths = defaultdict(list),
        handles = defaultdict(list)
    )

    for file in filestocopy:
        fileid, numcopies = file
        for _ in range(numcopies):
            uniquedir = tmp_path / str(uuid.uuid1())
            uniquedir.mkdir()
            newfile = tmp_path / uniquedir / sourcefiles.paths[fileid].name
            copyfile(sourcefiles.paths[fileid],newfile)
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
    return tmp_files

@fixture
def filesopen(copiedtestfiles):
    with ExitStack() as stack:
        copiedtestfiles.handles = {
            fileid: [stack.enter_context(open(path, 'rb')) for path in paths]
            for fileid, paths in copiedtestfiles.paths.items()
        }
        yield
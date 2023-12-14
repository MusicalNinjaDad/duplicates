from dataclasses import dataclass
from . import *

@mark.copyfiles(('fileA',2), ('fileA2',3))
def test_comparefilecontents(copiedtestfiles, filesopen):
    pathsandhandles = zip(
        (copiedtestfiles.paths['fileA'] + copiedtestfiles.paths['fileA2']),
        (copiedtestfiles.handles['fileA'] + copiedtestfiles.handles['fileA2'])
    )
    filestocompare = {frozenset(
        BufferedIOFile(path_handle[0], path_handle[1]) for path_handle in pathsandhandles
    )}
    identicalfiles = comparefilecontents(filestocompare)
    assert identicalfiles == {
        frozenset(BufferedIOFile(path) for path in copiedtestfiles.paths['fileA']),
        frozenset(BufferedIOFile(path) for path in copiedtestfiles.paths['fileA2'])
    }

@mark.copyfiles(('fileA',2), ('fileA2',1), ('fileB', 4))
def test_comparefilecontents_filehasnoduplicate(copiedtestfiles, filesopen):
    pathsandhandles = zip(
        (copiedtestfiles.paths['fileA'] + copiedtestfiles.paths['fileA2'] + copiedtestfiles.paths['fileB']),
        (copiedtestfiles.handles['fileA'] + copiedtestfiles.handles['fileA2'] + copiedtestfiles.handles['fileB'])
    )
    filestocompare = {frozenset(
        BufferedIOFile(path_handle[0], path_handle[1]) for path_handle in pathsandhandles
    )}
    identicalfiles = comparefilecontents(filestocompare)
    assert identicalfiles == {
        frozenset(BufferedIOFile(path) for path in copiedtestfiles.paths['fileA']),
        frozenset(BufferedIOFile(path) for path in copiedtestfiles.paths['fileB'])
    }

@mark.copyfiles(('fileA',2), ('fileB', 1), ('fileA2', 1))
@mark.linkfiles(('fileA',1))
def test_instantiatefrompath(copiedtestfiles):
    duplicatefiles = DuplicateFiles.frompaths(copiedtestfiles.root)
    assert any((
        duplicatefiles.duplicates == {frozenset((
                                BufferedIOFile(copiedtestfiles.paths['fileA'][1]),
                                BufferedIOFile(copiedtestfiles.paths['fileA'][0])
                                ))
                            },
        duplicatefiles.duplicates == {frozenset((
                                BufferedIOFile(copiedtestfiles.paths['fileA'][1]),
                                BufferedIOFile(copiedtestfiles.paths['fileA'][2])
                                ))
                            }
    )), f'Following files identified as duplicates: {duplicatefiles.duplicates}'


@mark.copyfiles(('fileA',2), ('fileA2',1), ('fileB', 4))
def test_instantiatefrompath_multipleduplicatefiles(copiedtestfiles):
    identicalfiles = DuplicateFiles.frompaths(copiedtestfiles.root)
    assert identicalfiles.duplicates == {
        frozenset(BufferedIOFile(path) for path in copiedtestfiles.paths['fileA']),
        frozenset(BufferedIOFile(path) for path in copiedtestfiles.paths['fileB'])
    }

@mark.copyfiles(('fileA',2), ('fileA2',1), ('fileB', 4))
def test_instantiatefrompath_zerosizefile(copiedtestfiles):
    with open(copiedtestfiles.root / Path("file0"), 'w'): pass
    identicalfiles = DuplicateFiles.frompaths(copiedtestfiles.root)
    assert identicalfiles.duplicates == {
        frozenset(BufferedIOFile(path) for path in copiedtestfiles.paths['fileA']),
        frozenset(BufferedIOFile(path) for path in copiedtestfiles.paths['fileB'])
    }

@mark.copyfiles(('fileA',2))
def test_multiplezerosizefiles(copiedtestfiles):
    zerolengthfilepaths = (
        copiedtestfiles.root / Path("file00"),
        copiedtestfiles.root / Path("file01")
    )
    
    for path in zerolengthfilepaths:
        with open(path, 'w'): pass

    identicalfiles = DuplicateFiles.frompaths(copiedtestfiles.root)
    assert identicalfiles.duplicates == {
        frozenset(BufferedIOFile(path) for path in copiedtestfiles.paths['fileA'])
    }

@mark.copyfiles(('fileA',2))
def test_instantiate_dropsymlinks(copiedtestfiles):
    fileA = copiedtestfiles.paths['fileA'][0]
    symlink = copiedtestfiles.root / Path('linktoA.txt')
    with skipon(OSError, lambda e: e.winerror == 1314, 'SymLinks not available on Windows without DevMode enabled'):
        symlink.symlink_to(fileA)
    duplicatefiles = DuplicateFiles.frompaths(copiedtestfiles.root)
    assert duplicatefiles.duplicates == {frozenset(path for path in copiedtestfiles.paths['fileA'])}, f'Following files identified as duplicates: {duplicatefiles.duplicates}'

@mark.copyfiles(('fileA',1), ('fileB',2))
@mark.linkfiles(('fileA',2))
def test_somefilesalreadyprocessed(copiedtestfiles):
    identicalfiles = DuplicateFiles.frompaths(copiedtestfiles.root)
    assert identicalfiles.duplicates == {
        frozenset(BufferedIOFile(path) for path in copiedtestfiles.paths['fileB'])
    }

@mark.copyfiles(
    set1 = (('fileA',1), ('fileB',2)),
    set2 = (('fileA2',2), ('fileB',2))
    )
def test_nocommonroot(copiedtestfiles):
    identicalfiles = DuplicateFiles.frompaths(
        copiedtestfiles['set1'].root,
        copiedtestfiles['set2'].root
    )

    fileA2 = frozenset(
        BufferedIOFile(path) 
        for path
        in copiedtestfiles['set2'].paths['fileA2']
    )


    fileB = frozenset(
        BufferedIOFile(path) 
        for path
        in copiedtestfiles['set1'].paths['fileB'] + copiedtestfiles['set2'].paths['fileB']
    )

    assert identicalfiles.duplicates == {fileA2, fileB}

@mark.copyfiles(
    set1 = (('fileA',1), ('fileB',2)),
    set2 = (('fileA2',2), ('fileB',2))
    )
def test_differentdevices(copiedtestfiles, monkeypatch):

    def _returnfakestat(*args, **kwargs):
        from datetime import datetime
        @dataclass
        class _fakestat():
            st_dev: int

        now = datetime.now().timestamp        

        return _fakestat(st_dev=now())

    monkeypatch.setattr(Path, 'stat', _returnfakestat)
    
    with raises(InvalidFileSystemError):
        _ = DuplicateFiles.frompaths(
            copiedtestfiles['set1'].root,
            copiedtestfiles['set2'].root
        )
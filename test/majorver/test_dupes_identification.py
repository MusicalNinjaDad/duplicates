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
    duplicatefiles = DuplicateFiles.frompath(copiedtestfiles.root)
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
    identicalfiles = DuplicateFiles.frompath(copiedtestfiles.root)
    assert identicalfiles.duplicates == {
        frozenset(BufferedIOFile(path) for path in copiedtestfiles.paths['fileA']),
        frozenset(BufferedIOFile(path) for path in copiedtestfiles.paths['fileB'])
    }

@mark.copyfiles(('fileA',2), ('fileA2',1), ('fileB', 4))
def test_instantiatefrompath_zerosizefile(copiedtestfiles):
    with open(copiedtestfiles.root / Path("file0"), 'w'): pass
    identicalfiles = DuplicateFiles.frompath(copiedtestfiles.root)
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

    identicalfiles = DuplicateFiles.frompath(copiedtestfiles.root)
    assert identicalfiles.duplicates == {
        frozenset(BufferedIOFile(path) for path in copiedtestfiles.paths['fileA'])
    }
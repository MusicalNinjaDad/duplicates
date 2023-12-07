from . import *

@mark.copyfiles(('fileA',2), ('fileA2',3))
def test_recursivecomparison(copiedtestfiles, filesopen):
    pathsandhandles = zip(
        (copiedtestfiles.paths['fileA'] + copiedtestfiles.paths['fileA2']),
        (copiedtestfiles.handles['fileA'] + copiedtestfiles.handles['fileA2'])
    )
    filestocompare = {frozenset(
        BufferedIOFile(path_handle[0], path_handle[1], chunksize = 4) for path_handle in pathsandhandles
    )}
    identicalfiles = DuplicateFiles.comparefilecontents(filestocompare)
    assert identicalfiles == {
        frozenset(BufferedIOFile(path, chunksize = 4) for path in copiedtestfiles.paths['fileA']),
        frozenset(BufferedIOFile(path, chunksize = 4) for path in copiedtestfiles.paths['fileA2'])
    }

@mark.copyfiles(('fileA',2), ('fileA2',1), ('fileB', 4))
def test_recursivecomparisonignoressingles(copiedtestfiles, filesopen):
    pathsandhandles = zip(
        (copiedtestfiles.paths['fileA'] + copiedtestfiles.paths['fileA2'] + copiedtestfiles.paths['fileB']),
        (copiedtestfiles.handles['fileA'] + copiedtestfiles.handles['fileA2'] + copiedtestfiles.handles['fileB'])
    )
    filestocompare = {frozenset(
        BufferedIOFile(path_handle[0], path_handle[1], chunksize = 4) for path_handle in pathsandhandles
    )}
    identicalfiles = DuplicateFiles.comparefilecontents(filestocompare)
    assert identicalfiles == {
        frozenset(BufferedIOFile(path, chunksize = 4) for path in copiedtestfiles.paths['fileA']),
        frozenset(BufferedIOFile(path, chunksize = 4) for path in copiedtestfiles.paths['fileB'])
    }

@mark.copyfiles(('fileA',2), ('fileB', 1), ('fileA2', 1))
@mark.linkfiles(('fileA',1))
def test_instantiatefrompath(copiedtestfiles):
    duplicatefiles = DuplicateFiles.frompath(copiedtestfiles.root)
    assert any((
        duplicatefiles.duplicates == {frozenset((
                                BufferedIOFile(copiedtestfiles.paths['fileA'][1], chunksize=4),
                                BufferedIOFile(copiedtestfiles.paths['fileA'][0], chunksize=4)
                                ))
                            },
        duplicatefiles.duplicates == {frozenset((
                                BufferedIOFile(copiedtestfiles.paths['fileA'][1], chunksize=4),
                                BufferedIOFile(copiedtestfiles.paths['fileA'][2], chunksize=4)
                                ))
                            }
    )), f'Following files identified as duplicates: {duplicatefiles.duplicates}'

@mark.copyfiles(('fileA',2), ('fileA2',1), ('fileB', 4))
def test_finddupesemutlipledupes(copiedtestfiles):
    identicalfiles = DuplicateFiles.frompath(copiedtestfiles.root)
    assert identicalfiles.duplicates == {
        frozenset(BufferedIOFile(path, chunksize = 4) for path in copiedtestfiles.paths['fileA']),
        frozenset(BufferedIOFile(path, chunksize = 4) for path in copiedtestfiles.paths['fileB'])
    }
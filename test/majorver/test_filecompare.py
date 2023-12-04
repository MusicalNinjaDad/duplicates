from . import filesofsamesize, BufferedIOFile, drophardlinks, finddupes, recursivecompare
from ...duplicates.dupes import _comparefilechunk
from ..testimports import *

@mark.copyfiles(('fileA',2))
def test_fileissamesize(copiedtestfiles):
    duplicatefiles = filesofsamesize(copiedtestfiles.root)
    assert duplicatefiles == {frozenset((copiedtestfiles.paths['fileA'][0], copiedtestfiles.paths['fileA'][1]))}

@mark.copyfiles(('fileA',2))
def test_samefilecontentsfirstchunk(copiedtestfiles, filesopen):
    filestocompare = frozenset(
        BufferedIOFile(path_handle[0], path_handle[1], chunksize=4) for path_handle in zip(copiedtestfiles.paths['fileA'], copiedtestfiles.handles['fileA'])
    )
    identicalfiles = _comparefilechunk(filestocompare)
    assert identicalfiles == {filestocompare}

@mark.copyfiles(('fileA',2))
def test_samefilecontentsstopsatEOF(copiedtestfiles, filesopen):
    filestocompare = frozenset(
        BufferedIOFile(path_handle[0], path_handle[1], chunksize=4) for path_handle in zip(copiedtestfiles.paths['fileA'], copiedtestfiles.handles['fileA'])
    )
    chunkcount = 0
    while True:
        try:
            identicalfiles = _comparefilechunk(filestocompare)
        except EOFError:
            break
        else:
            chunkcount += 1
    assert identicalfiles == {filestocompare}
    assert chunkcount == 4

@mark.copyfiles(('fileA',2), ('fileA2',3))
def test_recursivecomparison(copiedtestfiles, filesopen):
    pathsandhandles = zip(
        (copiedtestfiles.paths['fileA'] + copiedtestfiles.paths['fileA2']),
        (copiedtestfiles.handles['fileA'] + copiedtestfiles.handles['fileA2'])
    )
    filestocompare = {frozenset(
        BufferedIOFile(path_handle[0], path_handle[1], chunksize = 4) for path_handle in pathsandhandles
    )}
    identicalfiles = recursivecompare(filestocompare)
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
    identicalfiles = recursivecompare(filestocompare)
    assert identicalfiles == {
        frozenset(BufferedIOFile(path, chunksize = 4) for path in copiedtestfiles.paths['fileA']),
        frozenset(BufferedIOFile(path, chunksize = 4) for path in copiedtestfiles.paths['fileB'])
    }

@mark.copyfiles(('fileA',2))
@mark.linkfiles(('fileA',1))
def test_drophardlinks(copiedtestfiles):
    filestocompare = frozenset(path for path in copiedtestfiles.paths['fileA'])
    assert len(filestocompare) == 3
    identicalfiles = drophardlinks(filestocompare)
    assert len(identicalfiles) == 2
    assert copiedtestfiles.paths['fileA'][1] in identicalfiles
    assert any((
        copiedtestfiles.paths['fileA'][0] in identicalfiles,
        copiedtestfiles.paths['fileA'][2] in identicalfiles
    ))

@mark.copyfiles(('fileA',2), ('fileB', 1), ('fileA2', 1))
@mark.linkfiles(('fileA',1))
def test_integrate_list_compare(copiedtestfiles):
    duplicatefiles = finddupes(copiedtestfiles.root)    
    assert any((
        duplicatefiles == {frozenset((
                                BufferedIOFile(copiedtestfiles.paths['fileA'][1], chunksize=4),
                                BufferedIOFile(copiedtestfiles.paths['fileA'][0], chunksize=4)
                                ))
                            },
        duplicatefiles == {frozenset((
                                BufferedIOFile(copiedtestfiles.paths['fileA'][1], chunksize=4),
                                BufferedIOFile(copiedtestfiles.paths['fileA'][2], chunksize=4)
                                ))
                            }
    )), f'Following files identified as duplicates: {duplicatefiles}'

@mark.copyfiles(('fileA',2), ('fileA2',1), ('fileB', 4))
def test_finddupesemutlipledupes(copiedtestfiles):
    identicalfiles = finddupes(copiedtestfiles.root)
    assert identicalfiles == {
        frozenset(BufferedIOFile(path, chunksize = 4) for path in copiedtestfiles.paths['fileA']),
        frozenset(BufferedIOFile(path, chunksize = 4) for path in copiedtestfiles.paths['fileB'])
    }
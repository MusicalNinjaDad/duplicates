from . import *

@mark.copyfiles(('fileA',2), ('fileB', 1), ('fileA2', 1))
@mark.linkfiles(('fileA',1))
def test_inoindex(copiedtestfiles):
    duplicatefiles = DuplicateFiles.frompath(copiedtestfiles.root)
    assert duplicatefiles._inoindex == {
        copiedtestfiles.paths['fileA'][0].stat().st_ino: frozenset({
            copiedtestfiles.paths['fileA'][0],
            copiedtestfiles.paths['fileA'][2]
        }),
        copiedtestfiles.paths['fileA'][1].stat().st_ino: frozenset({
            copiedtestfiles.paths['fileA'][1]
        }),
        # copiedtestfiles.paths['fileB'][0].stat().st_ino: frozenset({
        #     copiedtestfiles.paths['fileB'][0]
        # }), -- Not in index as only file of this size => cannot be a duplicate
        copiedtestfiles.paths['fileA2'][0].stat().st_ino: frozenset({
            copiedtestfiles.paths['fileA2'][0]
        })
    }

@mark.copyfiles(('fileA',2), ('fileB', 1), ('fileA2', 1))
@mark.linkfiles(('fileA',1))
def test_uniqueinos(copiedtestfiles):
    duplicatefiles = DuplicateFiles.frompath(copiedtestfiles.root)
    assert all(
        path in duplicatefiles._uniqueinos
        for path in (
            copiedtestfiles.paths['fileA'][1],
            copiedtestfiles.paths['fileA2'][0])
        )
    assert any(
        path in duplicatefiles._uniqueinos
        for path in (
            copiedtestfiles.paths['fileA'][0],
            copiedtestfiles.paths['fileA'][2])
        )
    assert not all(
        path in duplicatefiles._uniqueinos
        for path in (
            copiedtestfiles.paths['fileA'][0],
            copiedtestfiles.paths['fileA'][2])
        )
from . import *

@mark.xfail(reason = 'Not Implemented')
@mark.copyfiles(('fileA',2), ('fileB', 1), ('fileA2', 1))
@mark.linkfiles(('fileA',1))
def test_inoindex(copiedtestfiles):
    duplicatefiles = DuplicateFiles.frompath(copiedtestfiles.root)
    assert duplicatefiles._inoindex == {
        copiedtestfiles.paths['fileA'][0].stat().st_ino: frozenset({
            copiedtestfiles['fileA'][0].path,
            copiedtestfiles['fileA'][2].path
        }),
        copiedtestfiles.paths['fileA'][1].stat().st_ino: frozenset({
            copiedtestfiles.paths['fileA'][1].path
        }),
        # copiedtestfiles.paths['fileB'][0].stat().st_ino: frozenset({
        #     copiedtestfiles.paths['fileB'][0].path
        # }), -- Not in index as only file of this size => cannot be a duplicate
        copiedtestfiles.paths['fileA2'][0].stat().st_ino: frozenset({
            copiedtestfiles.paths['fileA2'][0].path
        })
    }
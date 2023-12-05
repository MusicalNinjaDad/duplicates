from . import *

@mark.copyfiles(('fileA',2))
def test_replacecopywithlink(copiedtestfiles):
    assert copiedtestfiles.paths['fileA'][0].stat().st_ino != copiedtestfiles.paths['fileA'][1].stat().st_ino
    replacewithlink(copiedtestfiles.paths['fileA'][0], copiedtestfiles.paths['fileA'][1])
    assert copiedtestfiles.paths['fileA'][0].stat().st_ino == copiedtestfiles.paths['fileA'][1].stat().st_ino

@mark.copyfiles(('fileA',2),('fileB',3))
def test_findandreplacecopywithlinks(copiedtestfiles):
    linkdupes(copiedtestfiles.root)
    fileAino = copiedtestfiles.paths['fileA'][0].stat().st_ino
    fileBino = copiedtestfiles.paths['fileB'][0].stat().st_ino
    assert all(
        file.stat().st_ino == fileAino for file in copiedtestfiles.paths['fileA']
    )
    assert all(
        file.stat().st_ino == fileBino for file in copiedtestfiles.paths['fileB']
    )


@mark.xfail #Not Implemented
@mark.copyfiles(('fileA', 2), ('fileA-copy', 2))
@mark.linkfiles(('fileA', 2), ('fileA-copy', 2))
def test_linkwhenlinksalreadyexist(copiedtestfiles):
    linkdupes(copiedtestfiles.root)
    fileAino = copiedtestfiles.paths['fileA'][0].stat().st_ino
    inoscorrect = {(fileid, i): file.stat().st_ino == fileAino for fileid in ('fileA', 'fileA-copy') for i, file in enumerate(copiedtestfiles.paths[fileid])}
    assert all(
        inoscorrect.values()
    ), f'{inoscorrect}'
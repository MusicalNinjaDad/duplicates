from . import *

@mark.copyfiles(('fileA',2),('fileB',3))
def test_findandreplacecopywithlinks(copiedtestfiles):
    dupes = DuplicateFiles.frompath(copiedtestfiles.root)
    dupes.link()
    fileAino = copiedtestfiles.paths['fileA'][0].stat().st_ino
    fileBino = copiedtestfiles.paths['fileB'][0].stat().st_ino
    assert all(
        file.stat().st_ino == fileAino for file in copiedtestfiles.paths['fileA']
    )
    assert all(
        file.stat().st_ino == fileBino for file in copiedtestfiles.paths['fileB']
    )


@mark.copyfiles(('fileA', 2), ('fileA-copy', 2))
@mark.linkfiles(('fileA', 2), ('fileA-copy', 2))
def test_linkwhenlinksalreadyexist(copiedtestfiles):
    dupes = DuplicateFiles.frompath(copiedtestfiles.root)
    dupes.link()
    fileAino = copiedtestfiles.paths['fileA'][0].stat().st_ino
    inoscorrect = {(fileid, i): file.stat().st_ino == fileAino for fileid in ('fileA', 'fileA-copy') for i, file in enumerate(copiedtestfiles.paths[fileid])}
    assert all(
        inoscorrect.values()
    ), f'{inoscorrect}'
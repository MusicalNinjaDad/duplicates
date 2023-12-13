from . import *

@mark.copyfiles(('fileA',2),('fileB',3))
def test_link(copiedtestfiles):
    dupes = DuplicateFiles.frompaths(copiedtestfiles.root)
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
def test_link_duplicatefileswithmultiplegroupsoflinks(copiedtestfiles):
    """fileA and fileA-copy are identical and BOTH have multiple copies AND multiple hardlinks
    """
    dupes = DuplicateFiles.frompaths(copiedtestfiles.root)
    dupes.link()
    fileAino = copiedtestfiles.paths['fileA'][0].stat().st_ino
    inoscorrect = {(fileid, i): file.stat().st_ino == fileAino for fileid in ('fileA', 'fileA-copy') for i, file in enumerate(copiedtestfiles.paths[fileid])}
    assert all(
        inoscorrect.values()
    ), f'{inoscorrect}'

@mark.copyfiles(('fileA',1))
@mark.linkfiles(('fileA',2))
def test_donothingifonlylinks(copiedtestfiles, monkeypatch):
    class InvalidCallToReplaceWithLinkError(Exception):
            pass
    
    @contextmanager
    def _dontlink(keep, link):
        raise InvalidCallToReplaceWithLinkError
    
    from ...duplicates import dupes
    monkeypatch.setattr(dupes, "_replacewithlink", _dontlink)
    # Monkeypatch was validated by adding an extra set of files which did need linking
    
    duplicatefiles = DuplicateFiles.frompaths(copiedtestfiles.root)
    duplicatefiles.link()
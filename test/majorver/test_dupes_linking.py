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

    fileA2inos = [(f.stat.st_ino, f.path) for f in fileA2]
    fileBinos = [(f.stat.st_ino, f.path) for f in fileB]
    assert len({x[0] for x in fileA2inos}) == 2, f'{fileA2inos}'
    assert len({x[0] for x in fileBinos}) == 4, f'{fileBinos}'

    identicalfiles.link()

    fileA2inos = [(f.refreshstat().st_ino, f.path) for f in fileA2]
    fileBinos = [(f.refreshstat().st_ino, f.path) for f in fileB]
    assert len({x[0] for x in fileA2inos}) == 1, f'{fileA2inos}'
    assert len({x[0] for x in fileBinos}) == 1, f'{fileBinos}'

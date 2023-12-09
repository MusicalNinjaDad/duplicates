from subprocess import run
from . import *

pytestmark = mark.tox

@mark.copyfiles(('fileA',2),('fileB',3))
def test_link(copiedtestfiles):
    command = [
        'dupes',
        '--link',
        copiedtestfiles.root
    ]
    
    run(command)

    fileAino = copiedtestfiles.paths['fileA'][0].stat().st_ino
    fileBino = copiedtestfiles.paths['fileB'][0].stat().st_ino
    assert all(
        file.stat().st_ino == fileAino for file in copiedtestfiles.paths['fileA']
    )
    assert all(
        file.stat().st_ino == fileBino for file in copiedtestfiles.paths['fileB']
    )
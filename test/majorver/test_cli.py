from subprocess import run
from . import *

pytestmark = mark.tox

@mark.copyfiles(('fileA',2),('fileB',3))
def test_link(copiedtestfiles):
    command = [
        'dupes',
        '--link',
        os.fspath(copiedtestfiles.root)
    ]
    
    completed = run(command, capture_output=True)
    
    output = [
        '2 sets of duplicates found, totalling 5 files',
        f'Linking files in {copiedtestfiles.root}...'
    ]

    assert completed.stdout.decode().strip() == os.linesep.join(output)

    fileAino = copiedtestfiles.paths['fileA'][0].stat().st_ino
    fileBino = copiedtestfiles.paths['fileB'][0].stat().st_ino
    assert all(
        file.stat().st_ino == fileAino for file in copiedtestfiles.paths['fileA']
    )
    assert all(
        file.stat().st_ino == fileBino for file in copiedtestfiles.paths['fileB']
    )

@mark.copyfiles(('fileA',2),('fileB',3))
def test_nolink(copiedtestfiles):
    
    originalinos = {file.stat().st_ino for copies in copiedtestfiles.paths.values() for file in copies}

    command = [
        'dupes',
        os.fspath(copiedtestfiles.root)
    ]

    completed = run(command, capture_output=True)

    output = [
        '2 sets of duplicates found, totalling 5 files'
    ]

    assert completed.stdout.decode().strip() == '\n'.join(output)

    newinos = {file.stat().st_ino for copies in copiedtestfiles.paths.values() for file in copies}

    assert newinos == originalinos
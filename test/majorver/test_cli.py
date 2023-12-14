from subprocess import run
from . import *

pytestmark = mark.tox

@mark.copyfiles(('fileA',2),('fileB',3))
def test_link(copiedtestfiles):
    command = [
        'dupes',
        '--link',
        '-y',
        os.fspath(copiedtestfiles.root)
    ]
    
    completed = run(command, capture_output=True)
    
    output = [
        f'Initiating search of {copiedtestfiles.root}',
        f'Found 2 groups of same-sized files, totalling 5 files',
        f'Identified 0 pre-existing hard links, leaving 5 files for comparison',
        f'Will now begin comparing file contents, this may take some time',
        f'Identified 2 sets of duplicate files, totalling 5 files',
        f'Current usage: 101, future usage: 39, saving: 62',
        f'Linking files in {copiedtestfiles.root} ...',
        'Done'
    ]

    stderr = [removetimestamp(s.strip()) for s in completed.stderr.decode().strip().split('\n')]
    assert (
        stderr == output
    ), f'\nOutput: {stderr}\nExpected: {output}'

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
        f'Initiating search of {copiedtestfiles.root}',
        f'Found 2 groups of same-sized files, totalling 5 files',
        f'Identified 0 pre-existing hard links, leaving 5 files for comparison',
        f'Will now begin comparing file contents, this may take some time',
        f'Identified 2 sets of duplicate files, totalling 5 files',
        f'Current usage: 101, future usage: 39, saving: 62'
    ]

    stderr = [removetimestamp(s.strip()) for s in completed.stderr.decode().strip().split('\n')]
    assert (
        stderr == output
    ), f'\nOutput: {stderr}\nExpected: {output}'

    newinos = {file.stat().st_ino for copies in copiedtestfiles.paths.values() for file in copies}

    assert newinos == originalinos

def test_version():
    
    command = [
        'dupes',
        '--version'
    ]

    completed = run(command, capture_output=True)

    with open('./__version__') as versionfile:
        version = versionfile.readline()

    stdout = [s.strip() for s in completed.stdout.decode().strip().split('\n')]

    assert any(version in line for line in stdout)
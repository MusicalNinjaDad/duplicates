import os
from pytest import mark
from ...duplicates.cli import dupes
from click.testing import CliRunner

@mark.copyfiles(('fileA',2),('fileB',3))
def test_link(copiedtestfiles):
    clirunner = CliRunner()
    command = [
        '--link',
        os.fspath(copiedtestfiles.root)
    ]
    result = clirunner.invoke(dupes, command)

    output = [
        '2 sets of duplicates found, totalling 5 files',
        'current usage: 101, potential usage: 39, saving: 62',
        f'Linking files in {copiedtestfiles.root} ...'
    ]

    assert [s.strip() for s in result.output.strip().split('\n')] == output

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
    
    clirunner = CliRunner()
    command = [
        os.fspath(copiedtestfiles.root)
    ]

    result = clirunner.invoke(dupes, command)

    output = [
        '2 sets of duplicates found, totalling 5 files',
        'current usage: 101, potential usage: 39, saving: 62'
    ]

    assert [s.strip() for s in result.output.strip().split('\n')] == output

    newinos = {file.stat().st_ino for copies in copiedtestfiles.paths.values() for file in copies}

    assert newinos == originalinos
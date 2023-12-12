import os
from pytest import mark
from ...duplicates.cli import dupes
from click.testing import CliRunner

@mark.copyfiles(('fileA',2),('fileB',3))
def test_link(copiedtestfiles):
    clirunner = CliRunner()
    command = [
        '--link',
        '-y',
        os.fspath(copiedtestfiles.root)
    ]
    result = clirunner.invoke(dupes, command)

    output = [
        f'Initiating search of {copiedtestfiles.root}',
        f'Found 2 groups of same-sized files',
        f'Identified 0 pre-existing hard links',
        f'Will now begin comparing file contents, this may take some time',
        f'Identified 2 sets of duplicate files, totalling 5 files',
        f'Current usage: 101, future usage: 39, saving: 62',
        f'Linking files in {copiedtestfiles.root} ...'
    ]

    stdout = [s.strip() for s in result.output.strip().split('\n')]
    assert (
        stdout == output
    ), f'\nOutput: {stdout}\nExpected: {output}'

    fileAino = copiedtestfiles.paths['fileA'][0].stat().st_ino
    fileBino = copiedtestfiles.paths['fileB'][0].stat().st_ino
    assert all(
        file.stat().st_ino == fileAino for file in copiedtestfiles.paths['fileA']
    )
    assert all(
        file.stat().st_ino == fileBino for file in copiedtestfiles.paths['fileB']
    )

@mark.copyfiles(('fileA',2),('fileB',3))
def test_linkapproved(copiedtestfiles):
    clirunner = CliRunner()
    command = [
        '--link',
        os.fspath(copiedtestfiles.root)
    ]
    result = clirunner.invoke(dupes, command, input='y')

    output = [
        f'Initiating search of {copiedtestfiles.root}',
        f'Found 2 groups of same-sized files',
        f'Identified 0 pre-existing hard links',
        f'Will now begin comparing file contents, this may take some time',
        f'Identified 2 sets of duplicate files, totalling 5 files',
        f'Current usage: 101, future usage: 39, saving: 62',
        'Link files? [y/N]: y',
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
def test_link_abort(copiedtestfiles):

    originalinos = {file.stat().st_ino for copies in copiedtestfiles.paths.values() for file in copies}

    clirunner = CliRunner()
    command = [
        '--link',
        os.fspath(copiedtestfiles.root)
    ]
    result = clirunner.invoke(dupes, command, input='n')

    output = [
        f'Initiating search of {copiedtestfiles.root}',
        f'Found 2 groups of same-sized files',
        f'Identified 0 pre-existing hard links',
        f'Will now begin comparing file contents, this may take some time',
        f'Identified 2 sets of duplicate files, totalling 5 files',
        f'Current usage: 101, future usage: 39, saving: 62',
        'Link files? [y/N]: n',
        'Aborted!'
    ]

    stdout = [s.strip() for s in result.output.strip().split('\n')]
    assert stdout == output, f'Stdout: {stdout}'

    newinos = {file.stat().st_ino for copies in copiedtestfiles.paths.values() for file in copies}

    assert newinos == originalinos


@mark.copyfiles(('fileA',2),('fileB',3))
def test_nolink(copiedtestfiles):
    
    originalinos = {file.stat().st_ino for copies in copiedtestfiles.paths.values() for file in copies}
    
    clirunner = CliRunner()
    command = [
        os.fspath(copiedtestfiles.root)
    ]

    result = clirunner.invoke(dupes, command)

    output = [
        f'Initiating search of {copiedtestfiles.root}',
        f'Found 2 groups of same-sized files',
        f'Identified 0 pre-existing hard links',
        f'Will now begin comparing file contents, this may take some time',
        f'Identified 2 sets of duplicate files, totalling 5 files',
        f'Current usage: 101, future usage: 39, saving: 62'
    ]

    assert [s.strip() for s in result.output.strip().split('\n')] == output

    newinos = {file.stat().st_ino for copies in copiedtestfiles.paths.values() for file in copies}

    assert newinos == originalinos
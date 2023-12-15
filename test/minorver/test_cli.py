from dataclasses import dataclass
import os
from pytest import mark

from ..majorver.test_output import SEPARATOR
from ...duplicates import cli 
from click.testing import CliRunner
from . import removetimestamp

@mark.copyfiles(('fileA',2),('fileB',3))
def test_link(copiedtestfiles):
    clirunner = CliRunner(mix_stderr=False)
    command = [
        '--link',
        '-y',
        os.fspath(copiedtestfiles.root)
    ]
    result = clirunner.invoke(cli.dupes, command)

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

    stderr = [removetimestamp(s.strip()) for s in result.stderr.strip().split('\n')]
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
def test_linkapproved(copiedtestfiles):
    clirunner = CliRunner(mix_stderr=False)
    command = [
        '--link',
        os.fspath(copiedtestfiles.root)
    ]
    result = clirunner.invoke(cli.dupes, command, input='y')

    output = [
        f'Initiating search of {copiedtestfiles.root}',
        f'Found 2 groups of same-sized files, totalling 5 files',
        f'Identified 0 pre-existing hard links, leaving 5 files for comparison',
        f'Will now begin comparing file contents, this may take some time',
        f'Identified 2 sets of duplicate files, totalling 5 files',
        f'Current usage: 101, future usage: 39, saving: 62',
        'Link files? [y/N]:', #prompting to stderr doesn't echo input (including \n)
        f'Linking files in {copiedtestfiles.root} ...',
        'Done'
    ]

    stderr = [removetimestamp(s.strip()) for s in result.stderr.strip().split('\n')]
    assert stderr == output, f'\nOutput: {stderr}\nExpected: {output}'

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
    result = clirunner.invoke(cli.dupes, command, input='n')

    output = [
        f'Initiating search of {copiedtestfiles.root}',
        f'Found 2 groups of same-sized files, totalling 5 files',
        f'Identified 0 pre-existing hard links, leaving 5 files for comparison',
        f'Will now begin comparing file contents, this may take some time',
        f'Identified 2 sets of duplicate files, totalling 5 files',
        f'Current usage: 101, future usage: 39, saving: 62',
        'Link files? [y/N]: n',
        'Aborted!'
    ]

    stdout = [removetimestamp(s.strip()) for s in result.output.strip().split('\n')]
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

    result = clirunner.invoke(cli.dupes, command)

    output = [
        f'Initiating search of {copiedtestfiles.root}',
        f'Found 2 groups of same-sized files, totalling 5 files',
        f'Identified 0 pre-existing hard links, leaving 5 files for comparison',
        f'Will now begin comparing file contents, this may take some time',
        f'Identified 2 sets of duplicate files, totalling 5 files',
        f'Current usage: 101, future usage: 39, saving: 62'
    ]

    assert [removetimestamp(s.strip()) for s in result.output.strip().split('\n')] == output

    newinos = {file.stat().st_ino for copies in copiedtestfiles.paths.values() for file in copies}

    assert newinos == originalinos

@mark.copyfiles(('fileA',2),('fileB',3))
def test_list(copiedtestfiles):
    
    originalinos = {file.stat().st_ino for copies in copiedtestfiles.paths.values() for file in copies}
    
    clirunner = CliRunner(mix_stderr=False)
    command = [
        os.fspath(copiedtestfiles.root),
        '--list'
    ]

    result = clirunner.invoke(cli.dupes, command)

    expected_stderr = [
        f'Initiating search of {copiedtestfiles.root}',
        f'Found 2 groups of same-sized files, totalling 5 files',
        f'Identified 0 pre-existing hard links, leaving 5 files for comparison',
        f'Will now begin comparing file contents, this may take some time',
        f'Identified 2 sets of duplicate files, totalling 5 files',
        f'Current usage: 101, future usage: 39, saving: 62'
    ]

    stderr = [removetimestamp(s.strip()) for s in result.stderr.strip().split('\n')]
    assert stderr == expected_stderr

    stdout = [removetimestamp(s.strip()) for s in result.stdout.strip().split('\n')]
    assert len(stdout) == 6
    assert all(os.fspath(path.absolute()) in stdout for copies in copiedtestfiles.paths.values() for path in copies)
    assert SEPARATOR.strip() in stdout

    newinos = {file.stat().st_ino for copies in copiedtestfiles.paths.values() for file in copies}

    assert newinos == originalinos

@mark.copyfiles(
    set1 = (('fileA',1), ('fileB',2)),
    set2 = (('fileA2',2), ('fileB',2))
    )
def test_multiplepaths(copiedtestfiles):
    clirunner = CliRunner()
    command = [
        os.fspath(copiedtestfiles['set1'].root),
        os.fspath(copiedtestfiles['set2'].root)
    ]

    result = clirunner.invoke(cli.dupes, command)

    output = [
        f'Initiating search of {copiedtestfiles['set1'].root}, {copiedtestfiles['set2'].root}',
        f'Found 2 groups of same-sized files, totalling 7 files',
        f'Identified 0 pre-existing hard links, leaving 7 files for comparison',
        f'Will now begin comparing file contents, this may take some time',
        f'Identified 2 sets of duplicate files, totalling 6 files',
        f'Current usage: 124, future usage: 39, saving: 85'
    ]

    assert [removetimestamp(s.strip()) for s in result.output.strip().split('\n')] == output

@mark.copyfiles(
    set1 = (('fileA',1), ('fileB',2)),
    set2 = (('fileA2',2), ('fileB',2))
    )
def test_differentfilesystems(copiedtestfiles, monkeypatch):

    def _returnfakestat(*args, **kwargs):
        from uuid import uuid1
        @dataclass
        class _fakestat():
            st_dev: int

        return _fakestat(st_dev=uuid1())

    monkeypatch.setattr(cli.Path, 'stat', _returnfakestat)

    clirunner = CliRunner()
    command = [
        os.fspath(copiedtestfiles['set1'].root),
        os.fspath(copiedtestfiles['set2'].root)
    ]

    result = clirunner.invoke(cli.dupes, command)

    output = [
        f'{copiedtestfiles['set1'].root}, {copiedtestfiles['set2'].root} are not on the same filesystem',
        'Aborted!'
    ]

    assert [s.strip() for s in result.output.strip().split('\n')] == output
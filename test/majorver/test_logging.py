from . import *
import logging


@mark.copyfiles(('fileA', 2), ('fileB', 1), ('fileA2', 1))
@mark.linkfiles(('fileA', 1))
def test_instantiatefrompath(copiedtestfiles, caplog):
    caplog.set_level(logging.INFO, logger='dupes')
    _ = DuplicateFiles.frompath(copiedtestfiles.root)
    logs = [record for record in caplog.records if record.name.startswith(LOGROOT)]
    logmessages = [record.message for record in logs]

    expectedmessages = [
        f'Initiating search of {copiedtestfiles.root}',
        f'Found 1 groups of same-sized files'
    ]

    assert (
        logmessages == expectedmessages
    ), f'\nReceived log: {logmessages}\nExpected: {expectedmessages}\nMissing: {set(expectedmessages).difference(logmessages)}\nExtra: {set(logmessages).difference(expectedmessages)}'
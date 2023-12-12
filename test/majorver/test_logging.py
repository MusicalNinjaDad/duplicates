from . import *
import logging

@mark.copyfiles(('fileA',2), ('fileB', 1), ('fileA2', 1))
@mark.linkfiles(('fileA',1))
def test_instantiatefrompath(copiedtestfiles, caplog):
    caplog.set_level(logging.INFO, logger='dupes')
    _ = DuplicateFiles.frompath(copiedtestfiles.root)
    logs = [record for record in caplog.records if record.name.startswith(LOGROOT)]
    logmessages = [record.message for record in logs]
    assert f'Initiating search of {copiedtestfiles.root}' in logmessages
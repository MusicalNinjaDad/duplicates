from . import *

@mark.copyfiles(('fileA',2))
def test_replacecopywithlink(copiedtestfiles):
    assert copiedtestfiles.paths['fileA'][0].stat().st_ino != copiedtestfiles.paths['fileA'][1].stat().st_ino
    replacewithlink(copiedtestfiles.paths['fileA'][0], copiedtestfiles.paths['fileA'][1])
    assert copiedtestfiles.paths['fileA'][0].stat().st_ino == copiedtestfiles.paths['fileA'][1].stat().st_ino
from . import *

@mark.copyfiles(('fileA',2),('fileB',3))
def test_keywordarguments(copiedtestfiles):
    dupes = DuplicateFiles.frompaths(copiedtestfiles.root)
    with raises(TypeError):
        dupes.printout(True)
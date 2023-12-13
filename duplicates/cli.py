import logging
import os
from pathlib import Path
import sys
from click import argument, command, confirm, option

from . import DuplicateFiles, LOGROOT

_logger = logging.getLogger(LOGROOT)

@command()
@argument('rootdir')
@option('--link', is_flag=True)
@option('-y', 'approved', is_flag=True)
@option('--list', '_list', is_flag=True)
@option('--short', is_flag=True)
def dupes(rootdir, link, approved, _list, short):
    _logger.setLevel(logging.INFO)
    consoleoutput = logging.StreamHandler()
    consoleoutput.setLevel(logging.INFO)
    consoleoutput.setStream(sys.stderr)
    outputformat = logging.Formatter('%(asctime)s - %(message)s')
    consoleoutput.setFormatter(outputformat)
    _logger.addHandler(consoleoutput)

    rootdir = Path(rootdir)
    duplicatefiles = DuplicateFiles.frompath(rootdir)
    
    if short:
        print(duplicatefiles.printout(ignoresamenames=True))
    elif _list:
        print(duplicatefiles.printout())
    
    if link:
        if not approved:
            confirm('Link files?', abort=True, err=True) 
            print('', file=sys.stderr) #prompting to stderr doesn't echo input (including \n)
        _logger.info(f'Linking files in {os.fspath(rootdir)} ...')
        duplicatefiles.link()
        _logger.info(f'Done')
import logging
import os
from pathlib import Path
import sys
from click import Abort, argument, command, confirm, option, version_option

from . import DuplicateFiles, InvalidFileSystemError, LOGROOT

_logger = logging.getLogger(LOGROOT)

@command()
@argument('rootdirs', nargs=-1)
@option('--link', is_flag=True)
@option('-y', 'approved', is_flag=True)
@option('--list', '_list', is_flag=True)
@option('--short', is_flag=True)
@version_option(package_name='link_duplicates')
def dupes(rootdirs, link, approved, _list, short):
    _logger.setLevel(logging.INFO)
    consoleoutput = logging.StreamHandler()
    consoleoutput.setLevel(logging.INFO)
    consoleoutput.setStream(sys.stderr)
    outputformat = logging.Formatter('%(asctime)s - %(message)s')
    consoleoutput.setFormatter(outputformat)
    _logger.addHandler(consoleoutput)

    rootdirs = [Path(rootdir) for rootdir in rootdirs]
    
    try:
        duplicatefiles = DuplicateFiles.frompaths(*rootdirs)
    except InvalidFileSystemError:
        print(f'{', '.join(os.fspath(p) for p in rootdirs)} are not on the same filesystem')
        raise Abort
    
    if short:
        print(duplicatefiles.printout(ignoresamenames=True))
    elif _list:
        print(duplicatefiles.printout())
    
    if link:
        if not approved:
            confirm('Link files?', abort=True, err=True) 
            print('', file=sys.stderr) #prompting to stderr doesn't echo input (including \n)
        _logger.info(f'Linking files in {', '.join(os.fspath(p) for p in rootdirs)} ...')
        duplicatefiles.link()
        _logger.info(f'Done')
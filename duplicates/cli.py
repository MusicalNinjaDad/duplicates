import os
from pathlib import Path
from click import argument, command, confirm, option

from . import DuplicateFiles


@command()
@argument('rootdir')
@option('--link', is_flag=True)
@option('-y', 'approved', is_flag=True)
@option('--list', '_list', is_flag=True)
@option('--short', is_flag=True)
def dupes(rootdir, link, approved, _list, short):
    roodir = Path(rootdir)
    duplicatefiles = DuplicateFiles.frompath(roodir)
    
    sets = len(duplicatefiles.duplicates)
    totalfiles = len([file for group in duplicatefiles.duplicates for file in group])
    print(f'{sets} sets of duplicates found, totalling {totalfiles} files')
    
    totalsize = sum(file.stat.st_size for group in duplicatefiles.duplicates for file in group)
    futuresize = sum(next(iter(group)).stat.st_size for group in duplicatefiles.duplicates)
    print(f'current usage: {totalsize}, potential usage: {futuresize}, saving: {totalsize-futuresize}')
        
    if short:
        print(duplicatefiles.printout(ignoresamenames=True))
    elif _list:
        print(duplicatefiles.printout())
    
    if link:
        if not approved:
            confirm('Link files?', abort=True)
        print(f'Linking files in {os.fspath(rootdir)} ...')
        duplicatefiles.link()
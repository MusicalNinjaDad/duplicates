from pathlib import Path
from click import argument, command, option

from . import DuplicateFiles


@command()
@argument('rootdir')
@option('--link', is_flag=True)
@option('--list', '_list', is_flag=True)
@option('--short', is_flag=True)
def dupes(rootdir, link, _list, short):
    duplicatefiles = DuplicateFiles.frompath(Path(rootdir))
    
    sets = len(duplicatefiles.duplicates)
    totalfiles = len([file for group in duplicatefiles.duplicates for file in group])
    print(f'{sets} sets of duplicates found, totalling {totalfiles} files')
    
    if short:
        duplicatefiles.printout(ignoresamenames=True)
    elif _list:
        duplicatefiles.printout()    
    
    if link:
        print(f'Linking files in {rootdir}...')
        duplicatefiles.link()
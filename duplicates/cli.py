from pathlib import Path
from click import argument, command, option

from . import DuplicateFiles


@command()
@argument("rootdir")
@option("--link", is_flag=True)
def dupes(rootdir, link):
    duplicatefiles = DuplicateFiles.frompath(Path(rootdir))
    if link:
        print(f'I will link files in {rootdir}')
        duplicatefiles.link()

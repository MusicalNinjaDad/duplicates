from pathlib import Path

def _copy(self: Path, target: Path) -> None:
    from shutil import copytree
    if self.is_dir():
        copytree(self, target / self.name)
    else:
        raise NotImplementedError

Path.copy = _copy

def listfiles(in_path: Path) -> dict:
    allfiles = [root / file for root, dirs, files in in_path.walk() for file in files]
    filedict = dict()
    for file in allfiles:
        size = file.stat().st_size
        filedict[size] = [file]
    return filedict
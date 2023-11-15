from pathlib import Path

def _copy(self: Path, target: Path) -> None:
    from shutil import copytree
    if self.is_dir():
        copytree(self, target / self.name)
    else:
        raise NotImplementedError

Path.copy = _copy

def listfiles(in_path: Path) -> dict:
    filedict = dict()
    for root, dirs, files in in_path.walk():
        for file in files:
            filepath = root / file
            size = filepath.stat().st_size
            if size in filedict:
                filedict[size].append(filepath)
            else:
                filedict[size] = [filepath]
    return filedict
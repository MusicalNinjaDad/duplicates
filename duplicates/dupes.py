from pathlib import Path

def listfiles(in_path: Path) -> dict[int, set]:
    filedict = dict()
    for root, dirs, files in in_path.walk():
        for file in files:
            filepath = root / file
            size = filepath.stat().st_size
            if size in filedict:
                filedict[size].add(filepath)
            else:
                filedict[size] = {filepath}
    return filedict

def finddupes(filesbysize: dict[int, set]) -> set[frozenset]:
    dupes = {
        frozenset(filepath for filepath in files)
        for size, files in filesbysize.items() if len(files) > 1
    }
    return dupes
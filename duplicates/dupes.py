from pathlib import Path

def listfiles(in_path: Path) -> dict:
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
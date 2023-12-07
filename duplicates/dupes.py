from collections import defaultdict
from contextlib import ExitStack
import os
from pathlib import Path
from typing import Any, Callable, Iterable
from uuid import uuid1

from .bufferediofile import BufferedIOFile

class DuplicateFiles:
    @classmethod
    def comparefilecontents(cls, setstocompare: set[frozenset[BufferedIOFile]]) -> set[frozenset[BufferedIOFile]]:
        newsets = set()
        for setoffiles in setstocompare:
            newsets |= _comparefilechunk(setoffiles)
        try:
            return cls.comparefilecontents(newsets)
        except EOFError:
            return set(files for files in newsets)

def linkdupes(rootpath: Path) -> None:
    dupes = finddupes(rootpath)
    allpossibledupes = _filesofsamesize(rootpath)
    inoindex = _indexbyino({file for samesizeset in allpossibledupes for file in samesizeset })
    for setoffiles in dupes:
        fileiterator = iter(setoffiles)
        filetokeep = next(fileiterator).path
        for mainfiletolink in fileiterator:
            inotolink = inoindex[mainfiletolink.path.stat().st_ino]
            for filetolink in inotolink:
                replacewithlink(filetokeep, filetolink)

def finddupes(rootpath: Path) -> set[frozenset[BufferedIOFile]]:
    samesizefiles = _filesofsamesize(rootpath)
    dupes = set()
    for fileset in samesizefiles:
        inoindex = _indexbyino(fileset)
        nohardlinks = frozenset(next(iter(files)) for files in inoindex.values())
        fileobjects = {BufferedIOFile(filepath) for filepath in nohardlinks}
        with ExitStack() as stack:
            _ = [stack.enter_context(file.open()) for file in fileobjects]
            dupes |= DuplicateFiles.comparefilecontents({frozenset(fileobjects)})
    return dupes

def replacewithlink(keep: Path, replace: Path) -> None:
    def _extendpath(self: Path, string: Any) -> Path:
        return Path(''.join((str(self),str(string))))
    Path.__add__ = _extendpath

    tmplink = replace + '_' + uuid1()
    tmplink.hardlink_to(keep)
    os.replace(tmplink, replace)

def _sift(iterator: Iterable, siftby: Callable, onfail: Exception = ValueError) -> set[frozenset]:
    """Sifts an iterator and returns only those sets of values which share a common property
    - iterator: the iterator to sift
    - siftby: a Callable which when applied to each item in iterator returns the property to be used for sifting
    - onfail: the exception type to raise if siftby returns a Falsey result. Default: Value Error

    Returns: A set of frozensets, where all elements of each frozenset share the same property.
    Only sets with more than one item are returned - unique items are sifted out.
    """
    tmpdict = defaultdict(set)
    for item in iterator:
        idx = siftby(item)
        if idx: 
            tmpdict[idx].add(item)
        else:
            raise onfail
    return {frozenset(group) for group in tmpdict.values() if len(group) > 1}

def _filesofsamesize(pathtosearch: Path) -> set[frozenset[Path]]:
    """ Walks through all files in a path recursively and identifies those files which all have the same size.
    
    - pathtosearch: a Pathlib path to search recursively

    Returns a set of frozensets of Paths, where all items in each frozen set have the same size. Only returns groups which
    contain multiple files.
    """
    def _filepaths(in_path: Path):
        for root, dirs, files in in_path.walk():
            for file in files:
                filepath = root / file
                yield filepath
    
    dupes = _sift(_filepaths(pathtosearch), lambda p: p.stat().st_size)
    return dupes

def _comparefilechunk(filestocompare: frozenset[BufferedIOFile]) -> set[frozenset[BufferedIOFile]]:
    possibleduplicates = _sift(filestocompare, lambda f: f.readchunk(), EOFError)
    return possibleduplicates
    
def _indexbyino(filestoindex: frozenset[Path]) -> frozenset[Path]:    
    uniqueinos = defaultdict(set)
    for file in filestoindex:
        id = file.stat().st_ino
        uniqueinos[id].add(file)
    return uniqueinos
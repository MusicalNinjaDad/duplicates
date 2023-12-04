from collections import defaultdict, deque
from contextlib import ExitStack, contextmanager
from io import BufferedIOBase
import os
from pathlib import Path
from typing import Any, Callable, Iterable
from uuid import uuid1

class BufferedIOFile():
    """ A File that knows it's Path and is able to provide buffered read in chunks
    """
    MB = 1024**2

    def __init__(self, path: Path, handle: BufferedIOBase = None, chunksize: int = 100*MB):
        self.__path = path
        self.__handle = handle
        self.chunksize = chunksize        

    @property
    def path(self):
        return self.__path
    
    @property
    def handle(self):
        return self.__handle
    
    def __str__(self) -> str:
        return self.path

    def __repr__(self) -> str:
        return f'BufferedIOBase({self.path}, open: {self.handle is not None}, chunksize: {self.chunksize})'

    @contextmanager
    def open(self):
        with open(self.path, 'rb') as self.__handle: 
            yield
            self.__handle = None

    class _FileIterator():
        def __init__(self, handle: BufferedIOBase, chunksize: int) -> None:
            self.handle = handle
            self.chunksize = chunksize
        def __next__(self):
            chunk = self.handle.read(self.chunksize)
            if chunk:
                return chunk
            else:
                raise StopIteration

    def __iter__(self):
        self._iterator = self._FileIterator(self.handle, self.chunksize)
        return self._iterator

    def readchunk(self):
        """ Read the next chunk from the file (see also chunksize)
        Final chunk may not be full-size - will only include up to EOF
        Returns an empty binary string if EOF is passed (analog to file.read())
        """
        try:
            return next(self._iterator)
        except AttributeError:
            self._iterator = iter(self)
            return next(self._iterator)
        except StopIteration:
            return b''

    def __hash__(self) -> int:
        try:
            return self.cachedhash
        except AttributeError:
            self.cachedhash = hash(self.path)
            return self.cachedhash
        
    def __eq__(self, other: object) -> bool:
        return isinstance(other, (Path, BufferedIOFile)) and hash(self) == hash(other)


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


def filesofsamesize(pathtosearch: Path) -> set[frozenset]:
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


def comparefilecontents(setstocompare: set[frozenset[BufferedIOFile]]) -> set[frozenset[BufferedIOFile]]:
    newsets = set()
    for setoffiles in setstocompare:
        newsets |= _comparefilechunk(setoffiles)
    try:
        return comparefilecontents(newsets)
    except EOFError:
        return set(files for files in newsets)
    
def drophardlinks(filestocheck: frozenset[Path]) -> frozenset[Path]:    
    uniqueinos = defaultdict(lambda: deque(maxlen=1))
    for file in filestocheck:
        id = file.stat().st_ino
        uniqueinos[id] = file
    return frozenset(uniqueinos.values())
    
def finddupes(rootpath: Path) -> set[frozenset[BufferedIOFile]]:
    samesizefiles = filesofsamesize(rootpath)
    nohardlinks = {drophardlinks(files) for files in samesizefiles}
    dupes = set()
    for fileset in nohardlinks:
        fileobjects = {BufferedIOFile(filepath) for filepath in fileset}
        with ExitStack() as stack:
            _ = [stack.enter_context(file.open()) for file in fileobjects]
            dupes |= comparefilecontents({frozenset(fileobjects)})
    return dupes

def replacewithlink(keep: Path, replace: Path) -> None:
    def _extendpath(self: Path, string: Any) -> Path:
        return Path(''.join((str(self),str(string))))
    Path.__add__ = _extendpath

    tmplink = replace + '_' + uuid1()
    tmplink.hardlink_to(keep)
    os.replace(tmplink, replace)

def linkdupes(rootpath: Path) -> None:
    dupes = finddupes(rootpath)
    for setoffiles in dupes:
        fileiterator = iter(setoffiles)
        filetokeep = next(fileiterator).path
        for filetolink in fileiterator:
            replacewithlink(filetokeep, filetolink.path)
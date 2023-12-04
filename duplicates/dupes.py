from collections import defaultdict, deque
from contextlib import ExitStack, contextmanager
from io import BufferedIOBase
import os
from pathlib import Path
from typing import Any, Callable, Iterable
from uuid import uuid1

def groupby(iterator: Iterable, groupfunction: Callable) -> set[frozenset]:
    tmpdict = defaultdict(set)
    for item in iterator:
        tmpdict[groupfunction(item)].add(item)
    return {frozenset(group) for group in tmpdict.values() if len(group) > 1}


def filesofsamesize(pathtosearch: Path) -> set[frozenset]:
    def _filepaths(in_path: Path):
        for root, dirs, files in in_path.walk():
            for file in files:
                filepath = root / file
                yield filepath
    
    dupes = groupby(_filepaths(pathtosearch), lambda p: p.stat().st_size)
    return dupes

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

def comparefiles(filestocompare: frozenset[BufferedIOFile]) -> set[frozenset[BufferedIOFile]]:
    tempdict = defaultdict(set)
    for file in filestocompare:
        chunk = file.readchunk()
        if chunk:    
            tempdict[chunk].add(file)
        else: #EOF
            raise EOFError 
    possibleduplicates = set(frozenset(files) for chunk, files in tempdict.items())
    return possibleduplicates

def recursivecompare(setstocompare: set[frozenset[BufferedIOFile]]) -> set[frozenset[BufferedIOFile]]:
    newsets = set()
    for setoffiles in setstocompare:
        if len(setoffiles) == 1:
            pass
        else: 
            newsets |= comparefiles(setoffiles)
    try:
        return recursivecompare(newsets)
    except EOFError:
        return set(files for files in newsets if len(files) > 1) #if difference is only in last chunk ... otherwise EOF may be reached before len(setoffiles) == 1 depending on ordering in set
    
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
            dupes |= recursivecompare({frozenset(fileobjects)})
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
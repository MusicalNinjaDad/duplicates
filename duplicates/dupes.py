from collections import defaultdict
from contextlib import ExitStack
import logging
import os
from pathlib import Path
from typing import Any, Callable, Iterable
from uuid import uuid1

from .bufferediofile import BufferedIOFile, IsASymlinkError
from . import LOGROOT

class DuplicateFiles:

    @classmethod
    def frompath(cls, rootpath: Path):
        _logger = logging.getLogger(f'{LOGROOT}.frompath')
        _logger.info(f'Initiating search of {rootpath}')
        
        samesizefiles = _filesofsamesize(rootpath)
        allfiles = {file for fileset in samesizefiles for file in fileset}
        _logger.info(f'Found {len(samesizefiles)} groups of same-sized files, totalling {len(allfiles)} files')

        inoindex = _indexbyino(file for samesizeset in samesizefiles for file in samesizeset)
        uniqueinos = frozenset(next(iter(files)) for files in inoindex.values())
        _logger.info(f'Identified {len(allfiles)-len(uniqueinos)} pre-existing hard links, leaving {len(uniqueinos)} files for comparison')
        _logger.info(f'Will now begin comparing file contents, this may take some time')
        
        dupes = set()
        for fileset in samesizefiles:
            nohardlinks = fileset.intersection(uniqueinos)
            if len(nohardlinks) > 1:
                with ExitStack() as stack:
                    _ = [stack.enter_context(file.open()) for file in nohardlinks]
                    dupes |= comparefilecontents({frozenset(nohardlinks)})
                    
        alldupes = {file for fileset in dupes for file in fileset}
        totalsize = sum(file.stat.st_size for file in alldupes)
        futuresize = sum(next(iter(group)).stat.st_size for group in dupes)
        _logger.info(f'Identified {len(dupes)} sets of duplicate files, totalling {len(alldupes)} files')
        _logger.info(f'Current usage: {totalsize}, future usage: {futuresize}, saving: {totalsize-futuresize}')

        return DuplicateFiles(duplicates=dupes, inoindex=inoindex)

    def __init__(self, duplicates: set[frozenset[BufferedIOFile]], inoindex: dict[int: frozenset[Path]]) -> None:
        self.__duplicates = duplicates
        self.__inoindex = inoindex

    @property
    def duplicates(self):
        return self.__duplicates

    @property
    def _inoindex(self):
        return self.__inoindex
    
    def refreshinos(self):
        #if stale inos are ever going to be an issue this is probably how best to resolve
        raise NotImplementedError
    
    def link(self) -> None:
        for setoffiles in self.duplicates:
            fileiterator = iter(setoffiles)
            filetokeep = next(fileiterator)
            for mainfiletolink in fileiterator:
                inotolink = self._inoindex[mainfiletolink.stat.st_ino]
                for filetolink in inotolink:
                    _replacewithlink(filetokeep.path, filetolink.path)

    def printout(self, ignoresamenames: bool = False) -> str:
        separator = '\n=====================\n'
        def _countuniquenames(setoffiles):
            return len({file.path.name for file in setoffiles})
        def _fileperline(fileset: frozenset[BufferedIOFile]) -> str:
            return '\n'.join(str(file.path) for file in fileset)

        if ignoresamenames:
            interestinggroups = {
                fileset for fileset in self.duplicates
                if _countuniquenames(fileset) > 1
            }
        else:
            interestinggroups = self.duplicates

        return separator.join(_fileperline(fileset) for fileset in interestinggroups)

def comparefilecontents(setstocompare: set[frozenset[BufferedIOFile]]) -> set[frozenset[BufferedIOFile]]:
    comparisonstack = list(setstocompare)
    duplicates = set()
    while comparisonstack:
        setoffiles = comparisonstack.pop()
        try:
            comparisonstack.extend(_comparefilechunk(setoffiles))
        except EOFError:
            duplicates.add(setoffiles)
    return duplicates

def _replacewithlink(keep: Path, replace: Path) -> None:
    def _extendpath(self: Path, string: Any) -> Path:
        return Path(''.join((str(self),str(string))))
    Path.__add__ = _extendpath

    tmplink = replace + '_' + uuid1()
    tmplink.hardlink_to(keep)
    os.replace(tmplink, replace)

def _sift(iterator: Iterable, siftby: Callable, onfail: Exception = None) -> set[frozenset]:
    """Sifts an iterator and returns only those sets of values which share a common property
    - iterator: the iterator to sift
    - siftby: a Callable which when applied to each item in iterator returns the property to be used for sifting
    - onfail: the exception type to raise if siftby returns a Falsey result. Default: None, ignore the item

    Returns: A set of frozensets, where all elements of each frozenset share the same property.
    Only sets with more than one item are returned - unique items are sifted out.
    """
    tmpdict = defaultdict(set)
    for item in iterator:
        idx = siftby(item)
        if idx:
            tmpdict[idx].add(item)
        elif onfail: 
            raise onfail
        
            
    return {frozenset(group) for group in tmpdict.values() if len(group) > 1}

def _filesofsamesize(pathtosearch: Path) -> set[frozenset[BufferedIOFile]]:
    """ Walks through all files in a path recursively and identifies those files which all have the same size.
    
    - pathtosearch: a Pathlib path to search recursively

    Returns a set of frozensets of Paths, where all items in each frozen set have the same size. Only returns groups which
    contain multiple files.
    """
    def _bufferedfiles(in_path: Path):
        for root, dirs, files in in_path.walk(follow_symlinks=False):
            for file in files:
                filepath = root / file
                try:
                    yield BufferedIOFile(filepath)
                except IsASymlinkError:
                    pass
    
    dupes = _sift(_bufferedfiles(pathtosearch), lambda f: f.stat.st_size)
    return dupes

def _comparefilechunk(filestocompare: frozenset[BufferedIOFile]) -> set[frozenset[BufferedIOFile]]:
    possibleduplicates = _sift(filestocompare, lambda f: f.readchunk(), EOFError)
    return possibleduplicates
    
def _indexbyino(filestoindex: Iterable[BufferedIOFile]) -> dict[int: set[BufferedIOFile]]:
    uniqueinos = defaultdict(set)
    for file in filestoindex:
        id = file.stat.st_ino
        uniqueinos[id].add(file)
    return uniqueinos
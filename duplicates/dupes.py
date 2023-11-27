from io import BufferedIOBase
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

def filesofsamesize(filesbysize: dict[int, set]) -> set[frozenset]:
    dupes = {
        frozenset(filepath for filepath in files)
        for size, files in filesbysize.items() if len(files) > 1
    }
    return dupes

class BufferedIOFile():
    """ A File that knows it's Path and is able to provide buffered read in chunks
    """
    MB = 1024**2

    def __init__(self, path: Path, handle: BufferedIOBase, chunksize=100*MB):
        self.__path = path
        self.__handle = handle
        self.chunksize = chunksize        

    @property
    def path(self):
        return self.__path
    
    @property
    def handle(self):
        return self.__handle

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
    tempdict = {}
    for file in filestocompare:
        chunk = file.readchunk()
        if chunk:
            if chunk in tempdict:
                tempdict[chunk].add(file)
            else:
                tempdict[chunk] = {file}
        else: #EOF
            raise EOFError 
    possibleduplicates = set(frozenset(files) for chunk, files in tempdict.items())
    return possibleduplicates
    
def drophardlinks(filestocheck: frozenset[BufferedIOFile]) -> frozenset[BufferedIOFile]:    
    knownids = set()
    uniquefiles = set()
    for file in filestocheck:
        id = file.path.stat().st_ino
        if id in knownids:
            pass
        else:
            knownids.add(id)
            uniquefiles.add(file)
    return uniquefiles
    
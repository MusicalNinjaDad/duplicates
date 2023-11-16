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

    def __init__(self, path: Path, handle: BufferedIOBase = None, chunksize=100*MB):
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
        if self.handle is None:
            try:
                openedhandle = self.path.open('rb')
                return self._FileIterator(openedhandle, self.chunksize)
            except:
                openedhandle.close()
        else:
            return self._FileIterator(self.handle, self.chunksize)
        
    def __hash__(self) -> int:
        try:
            return self.cachedhash
        except AttributeError:
            self.cachedhash = hash(self.path)
            return self.cachedhash
        
    def __eq__(self, other: object) -> bool:
        return isinstance(other, (Path, BufferedIOFile)) and hash(self) == hash(other)
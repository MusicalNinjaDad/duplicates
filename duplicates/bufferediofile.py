from contextlib import contextmanager
from io import BufferedIOBase
import os
from pathlib import Path
from stat import *

class IsASymlinkError(ValueError):
    pass

class BufferedIOFile():
    """ A File that knows it's Path and is able to provide buffered read in chunks
    """
    MB = 1024**2

    def __init__(self, path: Path, handle: BufferedIOBase = None, chunksize: int = 100*MB, follow_symlinks=False):
        if follow_symlinks:
            raise NotImplementedError
        
        self.__stat = path.stat(follow_symlinks=follow_symlinks)
        if S_ISLNK(self.__stat.st_mode):
            raise IsASymlinkError('BufferedIOFile passed a symlink with follow_symlinks=False')
        
        self.__path = path.resolve()
        self.__handle = handle
        self.chunksize = chunksize        

    @property
    def path(self):
        return self.__path
    
    #TODO: Implement __fspath__ to make this PathLike
    
    @property
    def handle(self):
        return self.__handle
    
    @property
    def stat(self):
        try:
            return self.__stat
        except AttributeError:
            self.refreshstat()
            return self.__stat
        
    def refreshstat(self):
        self.__stat = self.path.stat()

    def __str__(self) -> str:
        return str(self.path)

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
        if isinstance(other, BufferedIOFile):
            return hash(self) == hash(other)
        else:
            try:
                return self.path == other.resolve()
            except AttributeError:
                pass
            try:
                return self.path == Path(os.fspath(other)).resolve()
            except TypeError:
                return False
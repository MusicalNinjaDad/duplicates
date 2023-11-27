from contextlib import ExitStack, contextmanager
from io import BufferedIOBase
from pathlib import Path

from recurtools import flatten

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
    
def finddupes(rootpath: Path) -> set[frozenset[BufferedIOFile]]:
    allfiles = {
        size: {BufferedIOFile(path) for path in setofpaths}
        for size, setofpaths in listfiles(rootpath).items()
    }
    nohardlinks = {
        size: drophardlinks(files)
        for size, files in allfiles.items()
        if len(files) > 1
    }
    return nohardlinks
    # with ExitStack() as stack:
    #     stack.enter_context(file.open() for files in allfiles.values() for file in files)
#     ================================== FAILURES ===================================
# _________________________ test_integrate_list_compare _________________________

# copiedtestfiles = Testfiles(root=WindowsPath('C:/Users/iammi/AppData/Local/Temp/pytest-of-iammi/pytest-59/test_integrate_list_compare0')...t_integrate_list_compare0/9a0e9011-8d5c-11ee-9fb3-10510787801a/fileB.txt')]}), handles=defaultdict(<class 'list'>, {}))

#     @mark.copyfiles(('fileA',2), ('fileB', 1))
#     @mark.linkfiles(('fileA',1))
#     def test_integrate_list_compare(copiedtestfiles):
# >       duplicatefiles = finddupes(copiedtestfiles.root)

# test\majorver\test_filecompare.py:54: 
# _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
# duplicates\dupes.py:120: in finddupes
#     stack.enter_context(file.open() for files in allfiles.values() for file in files)
# _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

# self = <contextlib.ExitStack object at 0x000001D4B17CF410>
# cm = <generator object finddupes.<locals>.<genexpr> at 0x000001D4B17BAA40>

#     def enter_context(self, cm):
#         """Enters the supplied context manager.
    
#         If successful, also pushes its __exit__ method as a callback and
#         returns the result of the __enter__ method.
#         """
#         # We look up the special methods on the type to match the with
#         # statement.
#         cls = type(cm)
#         try:
#             _enter = cls.__enter__
#             _exit = cls.__exit__
#         except AttributeError:
# >           raise TypeError(f"'{cls.__module__}.{cls.__qualname__}' object does "
#                             f"not support the context manager protocol") from None
# E           TypeError: 'builtins.generator' object does not support the context manager protocol

# ..\..\..\..\AppData\Local\Programs\Python\Python312\Lib\contextlib.py:512: TypeError
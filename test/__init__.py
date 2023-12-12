from .. import *
from pytest import mark, raises, skip

@contextmanager
def skipon(exceptiontype: Exception, check: callable = lambda x: True, reason: str = ''):
    """Skip test on Exception of type exceptiontype.
    Optionally run additional validation of exception before skipping.

    Arguments:
    - exceptiontype: the type of exception to skip
    - check (optional): a `callable` which returns a single `bool` value.
    Test will only be skipped if this check results `True`
    - reason (optional): reason to be passed to `skip` and included in the test logs

    Example:
    ```
    with skipon(OSError, lambda e: e.winerror == 1314, 'SymLinks not available on Windows without DevMode enabled')
        ...
    ```
    will skip test if Windows throws an OSError on missing permissions to create a symlink
    """
    
    try:
        yield
    except exceptiontype as e:
        if check(e): skip(reason=reason)
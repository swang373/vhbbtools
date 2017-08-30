import errno
import gzip
import os

import dill


def safe_makedirs(path):
    """Recursively create a directory without race conditions.

    This borrows from solutions to these Stack Overflow questions:
        * http://stackoverflow.com/a/5032238
        * http://stackoverflow.com/a/600612

    Parameters
    ----------
    path : path
        The path of the created directory.

    """
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def load_pkl(path):
    """Deserialize a Python object from disk.

    Parameters
    ----------
    path : path
        The input file path.

    Returns
    -------
    object
        The deserialized Python object.

    """
    _, ext = os.path.splitext(path)
    open_ = gzip.open if ext == '.pklz' else open
    with open_(path, 'rb') as f:
        obj = dill.load(f)
        return obj


def save_pkl(path, obj):
    """Serialize a Python object to disk.

    Parameters
    ----------
    path : path
        The output file path. The file is also compressed
        if the path ends with the .pklz file extension.
    obj : object
        The Python object to serialize.

    """
    _, ext = os.path.splitext(path)
    open_ = gzip.open if ext == '.pklz' else open
    with open_(path, 'wb') as f:
        dill.dump(obj, f)


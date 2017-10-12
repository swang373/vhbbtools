import errno
import glob
import os


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


def sorted_glob(pathname):
    """Return a sorted list of path names that match pathname.

    Otherwise, the glob module returns matching path names in
    arbitrary order because of its underlying usage of os.listdir().
    """
    return sorted(glob.iglob(pathname))


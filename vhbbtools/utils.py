import errno
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


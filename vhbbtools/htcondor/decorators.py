from .htcondorized import HTCondorized


def htcondorize(input_files=[], output_files=[]):
    """Enable calls to be transformed into HTCondor jobs.

    An HTCondorized object wraps a callable object or function. Calls to the
    HTCondorized object are forwarded to the wrapped callable, preserving the
    original signature when local execution is desired. For remote execution,
    the :meth:`queue` and :meth:`submit` methods provide the capability to
    submit calls as HTCondor jobs.

    The callable is wrapped by an HTCondorized object which preserves the
    original calling signature and provides the following methods:
        * :meth:`queue` : queues the positional and keyword arguments of calls
          that are submitted as HTCondor jobs.
        * :meth:`submit` : submits and consumes the queue of jobs.

    Parameters
    ----------
    input_files : list of paths, optional
        A list of paths to input files required by the callable. If the path
        is not absolute, it is assumed to be relative to the current working
        directory. The default is no input files.
    output_files : list of paths, optional
        A list of paths to output files created by the callable. The default
        is no output files.

    Returns
    -------
    HTCondorized
        The wrapped callable.

    """
    def wrapper(func):
        wrapped = HTCondorized(func, input_files, output_files)
        wrapped.__doc__ = func.__doc__
        return wrapped
    return wrapper


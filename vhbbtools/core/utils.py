import os
import subprocess

from concurrent import futures

from ..utils import safe_makedirs


class XRDCopyError(Exception):
    pass


def xrdcp(src, **kwargs):
    """Copy a file using the xrdcp command.

    Until the XRootD Python bindings are fully supported and stable in CMSSW,
    the copying functionality relies on the xrdcp executable.

    Parameters
    ----------
    src : path or url
        The path or remote url of the source file.
    dst : path or url, keyword only, optional
        The path or remote url of the destination.
        The default is the current working directory.
    force : bool, keyword only, optional
        A flag to allow existing copies to be overwritten.
        The default is False.
    """
    dst = kwargs.pop('dst', os.getcwd())
    force = kwargs.pop('force', False)
    if kwargs:
        raise TypeError('Unexpected keyword arguments: {!r}'.format(kwargs))
    command = ['xrdcp', '--path', '--posc', '--silent']
    if force:
        command.append('--force')
    command.extend([src, dst])
    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as e:
        raise XRDCopyError(str(e))


def multixrdcp(*srcs, **kwargs):
    """Copy files in parallel using the xrdcp command.

    Parameters
    ----------
    *srcs : paths or urls
        The paths or remote urls of the source files.
    dst : path or url, keyword only, optional
        The path or remote url of the destination.
        The default is the current working directory.
    force : bool, keyword only, optional
        A flag to allow existing copies to be overwritten.
        The default is False.
    """
    dst = kwargs.pop('dst', os.getcwd())
    force = kwargs.pop('force', False)
    if kwargs:
        raise TypeError('Unexpected keyword arguments: {!r}'.format(kwargs))
    with futures.ProcessPoolExecutor() as executor:
        fs = [executor.submit(xrdcp, src, dst=dst, force=force) for src in srcs]
    futures.wait(fs)


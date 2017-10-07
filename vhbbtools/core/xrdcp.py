import os
import subprocess

import concurrent.futures


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

    The xrdcp executable has a "--parallel" option, but limits the number of
    copy jobs to at most four. A ProcessPoolExecutor allows the maximum number
    of available cores to be utilized.

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
    with concurrent.futures.ProcessPoolExecutor() as executor:
        jobs = [executor.submit(xrdcp, src, dst=dst, force=force) for src in srcs]
        # If an exception is raised in a job, calling its result method will reraise
        # the exception without having to catch and reraise it ourselves.
        for job in concurrent.futures.as_completed(jobs):
            job.result()


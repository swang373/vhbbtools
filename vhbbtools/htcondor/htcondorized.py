import functools
import logging
import os
import shutil
import subprocess
import time

import appdirs
import jinja2
import pkg_resources

from ..utils import safe_makedirs
from .utils import save_pkl


LOGGER = logging.getLogger(__name__)


class HTCondorized(object):
    """A wrapper transforming calls into HTCondor jobs.

    An HTCondorized object wraps a callable object or function. Calls to the
    HTCondorized object are forwarded to the wrapped callable, preserving the
    original signature when local execution is desired. For remote execution,
    the :meth:`queue` and :meth:`submit` methods provide the capability to
    submit calls as HTCondor jobs.

    Parameters
    ----------
    func : callable
        A callable object.
    input_files : list of paths, optional
        A list of paths to input files required by the callable. If the path
        is not absolute, it is assumed to be relative to the current working
        directory. The default is no input files.
    output_files : list of paths, optional
        A list of paths to output files created by the callable. The default
        is no output files.

    """
    def __init__(self, func, input_files=[], output_files=[]):
        self.func = func
        self.input_files = [os.path.abspath(path) for path in input_files] or None
        self.output_files = output_files or None
        self._jobs = []
        self._templates = jinja2.Environment(
            loader=jinja2.PackageLoader('vhbbtools.htcondor', 'templates'),
            trim_blocks=True,
        )

    def __call__(self, *args, **kwargs):
        """Forward calls to the wrapped callable."""
        self.func(*args, **kwargs)

    def __repr__(self):
        return '{0}(func=\'{1}\', input_files=\'{2}\', output_files=\'{3}\')'.format(
            self.__class__.__name__,
            self.func,
            self.input_files,
            self.output_files,
        )

    def queue(self, *args, **kwargs):
        """Queue a call for submission as an HTCondor job.

        Parameters
        ----------
        *args
            Any positional arguments accepted by the wrapped callable.
        **kwargs
            Any keyword arguments accepted by the wrapped callable.

        """
        self._jobs.append((args, kwargs))

    def submit(self, name=None, commands={}, no_submit=False):
        """Submit the queued jobs and consume the current queue.

        The jobs are organized into a simple directed acyclic graph (DAG),
        where each job is represented as an independent node, and submitted
        to the HTCondor DAG Manager (DAGMan).

        Parameters
        ----------
        name : str, optional
            The name of the parent directory for the generated job submission
            files. The default is the current timestamp.
        commands : dict, optional
            HTCondor commands to include in the nodes' submit description file,
            in addition to the following which are handled automatically:
                * arguments
                * error
                * executable
                * getenv
                * log
                * output
                * queue
                * should_transfer_files
                * transfer_input_files
                * transfer_output_files
                * universe
            The default is no additional commands.
        no_submit : bool, optional
            If True, the job submission files are generated but not submitted
            to the HTCondor scheduler. The default is False.

        """
        # Create the directory tree for the job submission files.
        if not name:
            name = time.strftime('%Y%m%d_%H%M%S')
        user_data_dir = appdirs.user_data_dir(appname='vhbbtools')
        dagdir = os.path.join(user_data_dir, 'dags', self.func.__name__.lower(), name)
        jobdir = os.path.join(dagdir, 'jobs')
        logdir = os.path.join(dagdir, 'logs')
        safe_makedirs(jobdir)
        safe_makedirs(logdir)
        # Serialize the jobs and generate the job submission files.
        context = {
            'timestamp': time.strftime('%a %b %d %H:%M:%S %Z %Y'),
            'number_of_jobs': self._serialize_jobs(jobdir),
            'input_files': self.input_files,
            'output_files': self.output_files,
            'commands': commands,
            'environ': os.environ,
        }
        dag_path = os.path.join(dagdir, 'dag')
        self._generate_from_template('dag_input_file', dag_path, context)
        self._generate_from_template('node_submit_description', os.path.join(dagdir, 'node'), context)
        self._generate_from_template('worker.sh', os.path.join(dagdir, 'worker.sh'), context)
        run_script = pkg_resources.resource_filename(
            package_or_requirement='vhbbtools',
            resource_name='htcondor/templates/run.py',
        )
        shutil.copy(run_script, dagdir)
        # Unless otherwise directed, submit the DAG input file to DAGMan.
        if no_submit:
            LOGGER.info('HTCondor DAG input file generated but not submitted: %s', dag_path)
        else:
            subprocess.check_call(['condor_submit_dag', '-usedagdir', dag_path])

    def _serialize_jobs(self, jobdir):
        """Serialize the queued jobs and consume the current queue.

        For each job, a partial object is created by "freezing" the wrapped
        callable with the arguments supplied to the call. Calling this partial
        effectively executes the job. The partials are serialized to disk for
        transfer to worker nodes.

        Parameters
        ----------
        jobdir : path
            The output directory for the serialized jobs.

        Returns
        -------
        int
            The number of jobs serialized.

        """
        number_of_jobs = len(self._jobs)
        for i, (args, kwargs) in enumerate(self._jobs):
            save_pkl(
                path=os.path.join(jobdir, 'job{!s}.pklz'.format(i)),
                obj=functools.partial(self.func, *args, **kwargs),
            )
        del self._jobs[:]
        return number_of_jobs

    def _generate_from_template(self, name, path, context):
        """Generate a job submission file by rendering its template.

        Each job submission file has a corresponding template with variables
        that are rendered using the job submission arguments and environment.

        Parameters
        ----------
        name : str
            The name of the template. The available templates are:
                * dag_input_file
                * node_submit_description
                * worker.sh
                * run.py
        path : path
            The output file path.
        context : dict
            The mapping between job submission arguments and environment
            variables to the names of their corresponding template variables.

        """
        template = self._templates.get_template(name)
        with open(path, 'w') as f:
            f.write(template.render(context))


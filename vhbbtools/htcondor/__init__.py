"""
vhbbtools.htcondor
==================

This subpackage provides support for executing arbitrary Python code as batch
jobs using the HTCondor distributed computing framework.
"""

# Core classes
from .core import HTCondorized

# Decorators
from .decorators import htcondorize

__all__ = [
    # Core classes
    'HTCondorized',

    # Decorators
    'htcondorize',
]


"""
vhbbtools.conf
==============

This subpackage provides configuration classes
which handle the datasets used in an analysis.
"""

# Core classes
from .dataset import DatasetBase, MonteCarloBase

__all__ = [
    # Core classes
    'DatasetBase', 'MonteCarloBase',
]


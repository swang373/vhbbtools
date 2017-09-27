"""
vhbbtools.plotting
==================

This subpackage provides convenience classes and functions for creating
and styling plots according to the CMS Publication Committee standards.
"""

# Core classes
from .canvas import Canvas

from .labels import CMSLabel, LuminosityLabel

# Utilities
from .utils import draw_figure_labels

__all__ = [
    # Core classes
    'Canvas', 'CMSLabel', 'LuminosityLabel',

    # Utilities
    'draw_figure_labels',
]


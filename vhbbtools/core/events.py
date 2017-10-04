import logging
import os

import contextlib2
from rootpy import ROOT
from rootpy.context import thread_specific_tmprootdir
from rootpy.extern.shortuuid import uuid
from rootpy.io import TemporaryFile, root_open


LOGGER = logging.getLogger(__name__)


class EmptyEventlistError(Exception):
    pass


class Events(ROOT.TChain):
    """A subclass of TChain which handles events stored in VHiggsBB ntuples.
    """
    def __init__(self, *filenames, **kwargs):
        self.filenames = filenames
        self.tree_name = kwargs.get('tree_name', 'tree')
        super(Events, self).__init__(self.tree_name)
        for filename in self.filenames:
            self.Add(filename)

    def __repr__(self):
        return '{0}(filenames={1}, tree_name=\'{2}\')'.format(
            self.__class__.__name__,
            self.filenames,
            self.tree_name,
        )

    def download(self, dst):
        pass


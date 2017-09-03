import logging

import contextlib2
from rootpy import ROOT
from rootpy.context import thread_specific_tmprootdir
from rootpy.extern.shortuuid import uuid
from rootpy.io import TemporaryFile, root_open


LOGGER = logging.getLogger(__name__)


class EmptyEventlistError(Exception):
    pass


class Ntuple(ROOT.TChain):
    """A context manager for VHiggsBB ntuples.
    
    This is a subclass of TChain that provides a reusable context manager
    interface for handling a collection of VHiggsBB ntuples.

    Parameters
    ----------
    paths : paths
        The paths of the VHiggsBB ntuples.
    tree_name : str, optional
        The name of the TTree within the ntuples. The default is "tree".

    """
    def __init__(self, *paths, **kwargs):
        super(Ntuple, self).__init__(kwargs.get('tree_name', 'tree'))
        self.paths = paths
        # TODO: Add additional parameters for preselection, overall weight,
        # and per-event weights.

    def __enter__(self):
        """Set up the histogram attributes and chain the ntuples.
        """
        self._histogram_setup()
        for path in self.paths:
            self.Add(path)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Delete the histogram attributes and reset the eventlist.
        """
        self._histogram_teardown()
        if self.eventlist:
            self.eventlist = 0
        self.Reset()

    def __repr__(self):
        return '{0}(paths=\'{1}\', tree_name=\'{2}\')'.format(
            self.__class__.__name__,
            self.paths,
            self.tree_name,
        )

    def _generate_eventlist(self, selection):
        """Return the eventlist created by applying the selection.
        """
        name = uuid()
        with thread_specific_tmprootdir() as d:
            self.draw('>>{}'.format(name), selection)
            eventlist = d.Get(name)
            return eventlist

    def _histogram_setup(self):
        """Dynamically set the count and weight histograms summed
        across all files as attributes accessible by their name.
        """
        LOGGER.debug('Setting up count and weight histograms')
        self._histograms = []
        with contextlib2.ExitStack() as stack:
            files = [stack.enter_context(root_open(path)) for path in self.paths]
            for obj in files[0]:
                if isinstance(obj, ROOT.TH1):
                    name = obj.GetName()
                    hist = sum(f.Get(name) for f in files)
                    hist.SetName(name)
                    hist.SetDirectory(0)
                    setattr(self, name, hist)
                    LOGGER.debug('Attribute access enabled for histogram "{}"'.format(name))
                    self._histograms.append(hist)

    def _histogram_teardown(self):
        """Delete the histogram attributes.
        """
        LOGGER.debug('Cleaning up count and weight histograms')
        for hist in self._histograms:
            delattr(self, hist.GetName())
        del self._histograms

    @property
    def eventlist(self):
        return self.GetEventList()

    @eventlist.setter
    def eventlist(self, value):
        self.SetEventList(value)

    def activate(self, *branches):
        """Activate branches.

        Parameters
        ----------
        branches : strings
            The names of the branches to activate.
        """
        for branch in branches:
            self.SetBranchStatus(branch, 1)

    def count(self):
        """Count the number of events passing the selections.
        """
        name = uuid()
        branch = self.GetListOfBranches()[0].GetName()
        with thread_specific_tmprootdir() as d:
            self.draw('{0}=={0}>>{1}'.format(branch, name))
            hist = d.Get(name)
            return hist.Integral()

    def deactivate(self, *branches):
        """Deactivate branches.

        Parameters
        ----------
        branches : strings
            The names of the branches to deactivate.
        """
        for branch in branches:
            self.SetBranchStatus(branch, 0)

    def draw(self, expression, selection='', options='goff'):
        """A wrapper method for TChain.Draw which provides
        a calling signature that permits keyword arguments.
        """
        super(Ntuple, self).Draw(expression, selection, options)

    def iterselected(self):
        """A generator yielding only those events passing the current selection.
        """
        try:
            passing = set(self.eventlist.GetEntry(i) for i in xrange(self.eventlist.GetN()))
        except:
            raise EmptyEventlistError('iterselected called before applying selections')
        for i, event in enumerate(self):
            if i in passing:
                yield event

    def select(self, selection):
        """Apply a selection on the events. If previous selections were
        applied, only the subset of events passing them are considered.

        Parameters
        ----------
        selection : string
            The selection expression to apply, e.g. met_pt > 170.
        """
        eventlist_new = self._generate_eventlist(selection)
        if eventlist_new:
            if self.eventlist:
                eventlist_new.Intersect(self.eventlist)
            LOGGER.debug('{0!s} events pass the selection "{1}"'.format(eventlist_new.GetN(), selection))
            self.eventlist = eventlist_new

    def to_root(self, dst, optimize=False):
        """Save the collection of ntuples as a single ntuple consisting of the
        summed count and weight histograms and a single tree. If selections were
        applied, only the subset of events passing them are saved.

        Parameters
        ----------
        dst : path
            The path to the new ntuple.

        optimize : bool, optional
            Optimize the storage of the tree in the new ntuple. A temporary
            file is created containing a copy of the tree. The final tree is
            created as a clone of the copied tree with its baskets sorted by
            entry. Finally, the tree's baskets are reoptimized before it is
            written to the new ntuple. The default is False.
        """
        with root_open(dst, 'w') as outfile:
            for hist in self._histograms:
                hist.Write()
            if optimize:
                with TemporaryFile() as tmp:
                    tree_tmp = self.CopyTree('')
                    tmp.Write()
                    tmp.Flush()
                    outfile.cd()
                    tree_opt = tree_tmp.CloneTree(-1, 'fast SortBasketsByEntry')
                    tree_opt.OptimizeBaskets()
                    tree_opt.Write()
            else:
                tree_new = self.CopyTree('') if self.eventlist else self.CloneTree(-1, 'fast')
                tree_new.Write()


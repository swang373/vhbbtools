import array
import hashlib

import contextlib2
from rootpy import ROOT
from rootpy.context import thread_specific_tmprootdir
from rootpy.io import root_open


class Events(ROOT.TChain):
    """An interface for handling the events stored in VHiggsBB ntuples.

    This is implemented as a subclass of TChain.

    Parameters
    ----------
    *filenames : paths or urls
        The paths or urls of the ntuples to add to the chain.
    preselection : string, keyword only, optional
        The initial selection applied to the events immediately after the chain
        is created. The default is no preselection.
    ignore_branches : list of strings, keyword only, optional
        The names of the branches to deactivate immediately after the
        preselection has been applied to the events. The default is
        to keep all branches active.
    """
    def __init__(self, *filenames, **kwargs):
        self.preselection = kwargs.pop('preselection', None)
        self.ignore_branches = kwargs.pop('ignore_branches', [])
        if kwargs:
            raise TypeError('Unexpected keyword arguments: {!r}'.format(kwargs))
        super(Events, self).__init__('tree')
        self.filenames = filenames
        self._count_histograms = self._get_count_histograms()
        for filename in self.filenames:
            self.Add(filename)
        if preselection:
            self.select(preselection)
        self.deactivate(*self.ignore_branches)

    def __len__(self):
        """The total number of events in the TChain.
        """
        return self.GetEntries()

    def __repr__(self):
        return '{0}(preselection={1!r}, event_weight={2!r}, ignore_branches={3!r})'.format(
            self.__class__.__name__,
            self.filenames,
            self.preselection,
            self.ignore_branches,
        )

    def _create_eventlist(self, selection):
        """Return the eventlist created by a selection.
        """
        name = hashlib.md5(selection).hexdigest()
        # Keep the Draw method from polluting the current gDirectory.
        with thread_specific_tmprootdir() as d:
            self.draw('>>{0}'.format(name), selection)
            eventlist = d.GetName(name)
            return eventlist

    def _get_count_histograms(self):
        """Find any count histograms in the ntuples and set them as attributes.
        """
        count_histograms = []
        # The histograms are summed over all files.
        with contextlib2.ExitStack() as stack:
            files = [stack.enter_context(root_open(filename)) for filename in self.filenames]
            for obj in files[0]:
                if isinstance(obj, ROOT.TH1):
                    name = obj.GetName()
                    hist = sum(f.Get(name) for f in files)
                    hist.SetName(name)
                    hist.SetDirectory(0)
                    setattr(self, name, hist)
                    count_histograms.append(hist)
            return count_histograms

    @property
    def branches(self):
        """The branches in the TChain.
        """
        try:
            return list(self.GetListOfBranches())
        except TypeError:
            return []

    @property
    def eventlist(self):
        """The eventlist for the TChain.
        """
        return self.GetEventList()

    @eventlist.setter
    def eventlist(self, value):
        self.SetEventList(value)

    def activate(self, *branches, **kwargs):
        """Activate branches in the TChain.

        Parameters
        ----------
        *branches : strings
            The names of the branches to activate. Wildcarded TRegexp
            expressions such as "a*b" or "a*b*" are also valid. Unrecognized
            branches are ignored.
        exclusive : bool, keyword only, optional
            If True, all other branches are deactivated. The default is False.
        """
        exclusive = kwargs.pop('exclusive', False)
        if kwargs:
            raise TypeError('Unexpected keyword arguments: {!r}'.format(kwargs))
        if exclusive:
            self.SetBranchStatus('*', 0)
        # The "found" argument which is used to suppress warnings/errors
        # about unknown branches must be passed as an unsigned int.
        found = array.array('I', [1])
        for branch in branches:
            self.SetBranchStatus(branch, 1, found)

    def deactivate(self, *branches, **kwargs):
        """Deactivate branches in the TChain.

        Parameters
        ----------
        *branches : strings
            The names of the branches to deactivate. Wildcarded TRegexp
            expressions such as "a*b" or "a*b*" are also valid. Unrecognized
            branches are ignored.
        exclusive : bool, keyword only, optional
            If True, all other branches are activated. The default is False.
        """
        exclusive = kwargs.pop('exclusive', False)
        if kwargs:
            raise TypeError('Unexpected keyword arguments: {!r}'.format(kwargs))
        if exclusive:
            self.SetBranchStatus('*', 1)
        # The "found" argument which is used to suppress warnings/errors
        # about unknown branches must be passed as an unsigned int.
        found = array.array('I', [1])
        for branch in branches:
            self.SetBranchStatus(branch, 0, found)

    def draw(self, expression, selection='', options='goff'):
        """A wrapper for the Draw method that accepts keyword arguments.

        See the documentation of TTree.Draw for information.

        Parameters
        ----------
        expression : string
            The draw expression.
        selection : string, optional
            The selection expression.
        options : string, optional
            The draw options. The default is 'goff' to disable graphics.
        """
        super(Events, self).Draw(expression, selection, options)

    def select(self, selection):
        """Apply a selection on the events.

        If selections are already applied, only the current subset of passing
        events are considered.

        Parameters
        ----------
        selection : string
            The selection expression.
        """
        eventlist = self._create_eventlist(selection)
        if eventlist:
            if self.eventlist:
                eventlist.Intersect(self.eventlist)
            self.eventlist = eventlist


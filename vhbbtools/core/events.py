import array
import glob
import hashlib
import shutil
import tempfile

import contextlib2
from rootpy import ROOT
from rootpy.context import thread_specific_tmprootdir
from rootpy.io import TemporaryFile, root_open

from ..utils import sorted_glob
from .xrdcp import multixrdcp


class Events(ROOT.TChain):
    """A reusable context manager for handling VHiggsBB ntuples.

    Entering the context opens the files for reading, provides attribute
    access to count histograms, and sets the initial state by selecting
    events and deactivating branches if specified.
    
    Exiting the context resets the state, deletes the count histogram
    attributes, and closes the file handles.

    Parameters
    ----------
    *filenames : paths or urls
        The paths or urls of the ntuples.
    selection : string, keyword only, optional
        The selection applied to the events upon entering the context.
        The default is no selection.
    ignore_branches : list of strings, keyword only, optional
        The names of the branches to deactivate upon entering the context,
        after the initial selection has been applied. The default is to
        keep all branches active.
    download : bool, keyword only, optional
        Copy remote files to a local temporary directory and open the copies
        for reading instead. The default is to read remote files directly using
        the XRootD protocol.
    """
    def __init__(self, *filenames, **kwargs):
        self.selection = kwargs.pop('selection', None)
        self.ignore_branches = kwargs.pop('ignore_branches', [])
        self.download = kwargs.pop('download', False)
        if kwargs:
            raise TypeError('Unexpected keyword arguments: {!r}'.format(kwargs))
        super(Events, self).__init__('tree')
        self.filenames = filenames

    def __enter__(self):
        self._set_count_histogram_attributes()
        filenames = self._download_files() if self.download else self.filenames
        for filename in filenames:
            self.Add(filename)
        if self.selection:
            self.select(self.selection)
        self.deactivate(*self.ignore_branches)
        return self

    def __exit__(self):
        self._cleanup()
        self.eventlist = 0
        self.Reset()

    def __len__(self):
        """The total number of events."""
        return self.GetEntries()

    def _cleanup(self):
        """Clean up any count histogram attributes and downloaded files."""
        if self.download:
            #shutil.rmtree(self._tmpdir)
            del self._tmpdir
        for hist in self._count_histograms:
            delattr(self, hist.GetName())
        del self._count_histograms

    def _create_eventlist(self, selection):
        """Return the eventlist created for a selection."""
        name = hashlib.md5(selection).hexdigest()
        # Prevent the Draw method from modifying the current gDirectory.
        with thread_specific_tmprootdir() as d:
            self.draw('>>{0}'.format(name), selection)
            eventlist = d.GetName(name)
            return eventlist

    def _download_files(self):
        """Download the files to a temporary directory and return their paths."""
        self._tmpdir = tempfile.mkdtemp()
        multixrdcp(*self.filenames, dst=self._tmpdir)
        return sorted_glob('{0}/*'.format(self._tmpdir))

    def _set_count_histogram_attributes(self):
        """Set the count histograms as attributes accessible by their name."""
        self._count_histograms = []
        # Aggregate the count histograms across all files.
        with contextlib2.ExitStack() as stack:
            files = [stack.enter_context(root_open(filename)) for filename in self.filenames]
            for obj in files[0]:
                if isinstance(obj, ROOT.TH1):
                    name = obj.GetName()
                    hist = sum(f.Get(name) for f in files)
                    hist.SetName(name)
                    hist.SetDirectory(0)
                    setattr(self, name, hist)
                    self._count_histograms.append(hist)

    @property
    def branches(self):
        """The list of branches."""
        try:
            return list(self.GetListOfBranches())
        except TypeError:
            return []

    @property
    def eventlist(self):
        """The current eventlist."""
        return self.GetEventList()

    @eventlist.setter
    def eventlist(self, value):
        self.SetEventList(value)

    def activate(self, *branches, **kwargs):
        """Activate branches.

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
        """Deactivate branches.

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

    def count(self):
        """Return the number of events that pass the selections applied."""
        branch = self.branches[0].GetName()
        with thread_specific_tmprootdir() as d:
            self.draw('{0}=={0}>>count'.format(branch))
            hist = d.Get('count')
            return hist.Integral()

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

    def iterselected(self):
        """Yield the events that pass the selections applied."""
        try:
            passing = set(self.eventlist.GetEntry(i) for i in xrange(self.eventlist.GetN()))
        except ReferenceError:
            # If no selections are applied, yield all events.
            for event in self:
                yield event
        else:
            for i, event in enumerate(self):
                if i in passing:
                    yield event

    def select(self, selection):
        """Apply a selection on the events.

        If selections have already been applied, only the
        current subset of passing events are considered.

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

    def to_root(self, dst, optimize=False):
        """Write the selected events and count histograms to a ROOT file.
        
        Parameters
        ----------
        dst : path
            The path of the output ROOT file.
        optimize : bool, optional
            If True, optimize the storage of events in the output ROOT file.
            The default is False.
        """
        with root_open(dst, 'w') as outfile:
            for hist in self._count_histograms:
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


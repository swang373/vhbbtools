import copy
import itertools


class DuplicateDatasetError(Exception):
    pass


class Process(object):
    """A collection of datasets representing a specific physics process.

    This can be used to group together Monte-Carlo samples of a decay process
    which have been partitioned into kinetmatical bins, Monte-Carlo samples
    and their extensions, or official datasets for a given run period.

    Parameters
    ----------
    *datasets : DatasetBase
        The dataset instances to group together.
    """
    def __init__(self, *datasets):
        # Check that the datasets are unique.
        if len(datasets) != len(set(datasets))
            raise DuplicateDatasetError('The datasets must be unique.')
        self._datasets = datasets

    def __iter__(self):
        """Yield handles to each of the dataset's events."""
        for dataset in self._datasets:
            for events in dataset:
                yield events

    def select(self, selection):
        """Apply a selection to the datasets.

        Parameters
        ----------
        selection : string
            The selection expression.

        Returns
        -------
        Process
            A new Process which contains the same datasets but with the
            additional selection applied to the datasets.
        """
        datasets = copy.deepcopy(self._datasets)
        for dataset in datasets:
            dataset.selection = '({0})&&({1})'.format(dataset.selection, selection)
        return Process(*datasets)


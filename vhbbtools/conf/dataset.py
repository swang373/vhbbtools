from __future__ import division

import itertools
import re

import cached_property

from .. import Events
from .utils import (
    get_dataset_record_from_dbs,
    get_file_records_from_dbs,
)


# Aliases for the urls of the global and regional XRootD redirector servers.
XROOTD_REDIRECTORS = {
    'global': 'cms-xrd-global.cern.ch',
    'fnal': 'cmsxrootd.fnal.gov',
    'infn': 'xrootd-cms.infn.it',
}


class DatasetError(Exception):
    pass


class DatasetBase(object):
    """The base class for Dataset classes.

    User-defined Dataset classes should inherit from this base class
    and override the following class attributes:

    name : string
        The fully qualified dataset name of the format
        "/primary_dataset/processed_dataset/data_tier".
    dbs_instance : string
        One of the following DBS server instances where the dataset is
        registered:
            * global (default)
            * phys01
            * phys02
            * phys03
            * caf
    files : list of paths or urls, optional
        The paths or urls of the dataset's files.

    Iterating over a Dataset instance yields handles to the events contained
    in the files registered on DBS. This behaviour is altered by overriding
    the :attr:`files` attribute and providing explicit paths or urls.

    Parameters
    ----------
    selection : string, optional
        An initial selection applied to the dataset's events.
    chunk_size : numeric, optional
        The maximum chunk size in megabytes (MB) when iterating over the
        dataset's events. The chunk size is defined as the sum over the sizes
        of the dataset's files passed to the event handler. This is ignored
        when overriding the :attr:`files` attribute. The default is 2000 MB.
    valid : bool, optional
        Only iterate over files marked as valid on DBS. This is ignored when
        overriding the :attr:`files` attribute. The default is True.
    redirector : string, optional
        One of the following aliases for the XRootD redirectors used to locate
        and access the dataset's files:
            * global (default)
            * fnal
            * infn
        This is ignored when overriding the :attr:`files` attribute.
    """
    # The dataset name format regular expression.
    DATASET_NAME_RE = re.compile(r'^/\S+/\S+/\S+$')

    # The fully qualified dataset name of the format
    # "/primary_dataset/processed_dataset/data_tier".
    name = None

    # The DBS server instance where the dataset is registered.
    # This defaults to "global".
    dbs_instance = 'global'

    # The user-defined paths or urls of the dataset's files.
    files = None

    def __init__(self, selection=None, chunk_size=2000, redirector='global', valid=True):
        self.redirector = XROOTD_REDIRECTORS.get(redirector)
        self.selection = selection
        self.chunk_size = chunk_size
        self.valid = valid

    def __eq__(self, other):
        return isinstance(other, DatasetBase) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __iter__(self):
        """An iterator yielding handles to the dataset's events."""
        if self.files is None:
            if self.redirector is None:
                raise DatasetError('A valid XRootD redirector url is required to access remote files.')
            else:
                template_url = 'root://{0}//{{0}}'.format(self.redirector)

            if self.valid:
                records = itertools.ifilter(lambda record: record.is_file_valid, self.dbs_file_records)
            else:
                records = iter(self.dbs_file_records)

            chunk, current_size = [], 0
            for record in records:
                url = template_url.format(record.logical_file_name)
                file_size_in_MB = record.file_size / 1000000
                if current_size + file_size_in_MB > self.chunk_size:
                    yield Events(*chunk, selection=self.selection)
                    chunk = [url]
                    current_size = file_size_in_MB
                else:
                    chunk.append(url)
                    current_size += file_size_in_MB
            yield Events(*chunk, selection=self.selection)

        else:
            for files in self.files:
                yield files

    def _validate_dataset_name(self):
        if self.name is None or not self.DATASET_NAME_RE.match(self.name):
            raise DatasetError(
                'The class attribute "name" must refer to a fully qualified dataset '
                'name of the form "/primary_dataset/processed_dataset/data_tier"'
            )

    @cached_property.cached_property
    def dbs_dataset_record(self):
        """The dataset's information registered with DBS."""
        self._validate_dataset_name()
        return get_dataset_record_from_dbs(dataset=self.name, instance=self.dbs_instance)

    @cached_property.cached_property
    def dbs_file_records(self):
        """The dataset's file information registered with DBS."""
        self._validate_dataset_name()
        return get_file_records_from_dbs(dataset=self.name, instance=self.dbs_instance)


class MonteCarloBase(DatasetBase):
    """The base class for MonteCarlo classes.

    User-defined MonteCarlo classes should inherit from this base class
    and override the following class attributes:

    name : string
        The fully qualified dataset name of the format
        "/primary_dataset/processed_dataset/data_tier".
    cross_section : numeric
        The cross section of the Monte Carlo sample in units of picobarns (pb).
    dbs_instance : string
        One of the following DBS server instances where the dataset is
        registered:
            * global (default)
            * phys01
            * phys02
            * phys03
            * caf
    files : list of paths or urls, optional
        The paths or urls of the dataset's files.

    Iterating over a MonteCarlo instance yields handles to the events contained
    in the files registered on DBS. This behaviour is altered by overriding
    the :attr:`files` attribute and providing explicit paths or urls.

    Parameters
    ----------
    selection : string, optional
        An initial selection applied to the dataset's events.
    chunk_size : numeric, optional
        The maximum chunk size in megabytes (MB) when iterating over the
        dataset's events. The chunk size is defined as the sum over the sizes
        of the dataset's files passed to the event handler. This is ignored
        when overriding the :attr:`files` attribute. The default is 2000 MB.
    valid : bool, optional
        Only iterate over files marked as valid on DBS. This is ignored when
        overriding the :attr:`files` attribute. The default is True.
    redirector : string, optional
        One of the following aliases for the XRootD redirectors used to locate
        and access the dataset's files:
            * global (default)
            * fnal
            * infn
        This is ignored when overriding the :attr:`files` attribute.
    """
    # The cross section in units of picobarns (pb).
    cross_section = None


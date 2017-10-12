from __future__ import division

import itertools
import re

import cached_property

from .dbs import (
    get_dataset_record_from_dbs,
    get_file_records_from_dbs,
)
from .events import Events


# Aliases for the urls of the global and regional XRootD redirector servers.
XROOTD_REDIRECTORS = {
    'global': 'cms-xrd-global.cern.ch',
    'fnal': 'cmsxrootd.fnal.gov',
    'infn': 'xrootd-cms.infn.it',
}


class DatasetError(Exception):
    pass


class Dataset(object):
    """The abstract Dataset class.

    Concrete subclasses are defined by overriding the following class attributes:

    name : string
        The fully qualified name of the dataset of the form
        "/primary_dataset/processed_dataset/data_tier".
        The wildcard character "*" is not permitted.
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
    cross_section : numeric, optional
        The cross section in units of picobarns (pb). This attribute should
        only be overridden for datasets which are Monte Carlo samples.

    Iterating over a Dataset yields handles to the events contained in the files
    registered on DBS unless the :attr:`files` attribute is overridden.

    Parameters
    ----------
    selection : string, optional
        An initial selection applied to the dataset's events.
    chunk_size : numeric, optional
        The maximum chunk size in megabytes (MB) for iterating over the
        dataset's events. The chunk size is defined as the sum of the sizes
        of the dataset's files passed to the event handler. This is ignored
        when overriding the :attr:`files` attribute. The default is 2000 MB.
    valid : bool, optional
        Only iterate over files marked as valid on DBS. This is ignored when
        overriding the :attr:`files` attribute. The default is True.
    redirector : string, optional
        The url of the XRootD redirector server used to locate and access
        the dataset's files. The following regional redirector aliases are
        also recognized:
            * global (default)
            * fnal
            * infn
        This is ignored when overriding the :attr:`files` attribute.
    """
    # The dataset name format regular expression.
    DATASET_NAME_FORMAT_RE = re.compile(r'^/\S+/\S+/\S+$')

    # The fully qualified dataset name of the format
    # "/primary_dataset/processed_dataset/data_tier".
    name = None

    # The DBS server instance where the dataset is registered.
    # This defaults to "global".
    dbs_instance = 'global'

    # The user-defined paths or urls of the dataset's files.
    files = None

    # The cross section in units of picobarns (pb).
    # This is only applicable to Monte Carlo samples.
    cross_section = None

    def __init__(self, selection=None, chunk_size=2000, redirector=None, valid=True):
        self._validate_dataset_name()
        self.selection = selection
        self.chunk_size = chunk_size
        if redirector in XROOTD_REDIRECTORS:
            self.redirector = XROOTD_REDIRECTORS[redirector]
        else:
            self.redirector = redirector or XROOTD_REDIRECTORS['global']
        self.valid = valid

    def __eq__(self, other):
        return isinstance(other, Dataset) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __iter__(self):
        """Yield handles to the dataset's events in chunks."""
        if self.files is None:
            if self.redirector is None:
                raise DatasetError('A valid XRootD redirector url is required to access remote files.')
            else:
                file_url_template = 'root://{0}//{{0}}'.format(self.redirector)
            if self.valid:
                records = itertools.ifilter(lambda record: record.is_file_valid, self.dbs_file_records)
            else:
                records = iter(self.dbs_file_records)
            chunk, current_size = [], 0
            for record in records:
                file_url = file_url_template.format(record.logical_file_name)
                file_size_in_MB = record.file_size / 1000000
                if current_size + file_size_in_MB > self.chunk_size:
                    yield Events(*chunk, selection=self.selection)
                    chunk = [file_url]
                    current_size = file_size_in_MB
                else:
                    chunk.append(file_url)
                    current_size += file_size_in_MB
            yield Events(*chunk, selection=self.selection)

        else:
            for f in self.files:
                yield f

    def _validate_dataset_name(self):
        if self.name is None or not self.DATASET_NAME_FORMAT_RE.match(self.name) or '*' in self.name:
            raise DatasetError(
                'The class attribute "name" must reference a fully qualified '
                'dataset name which does not contain wildcard characters.'
            )

    @property
    def datatype(self):
        """The datatype is "mc" for Monte Carlo and "data" for data."""
        return 'mc' if self.cross_section else 'data'

    @cached_property.cached_property
    def dbs_dataset_record(self):
        """The dataset's information registered with DBS."""
        return get_dataset_record_from_dbs(dataset=self.name, instance=self.dbs_instance)

    @cached_property.cached_property
    def dbs_file_records(self):
        """The dataset's file information registered with DBS."""
        return get_file_records_from_dbs(dataset=self.name, instance=self.dbs_instance)


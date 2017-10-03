import re

from .utils import (
    cached_class_property,
    get_dataset_record_from_dbs,
    get_file_records_from_dbs,
)


DATASET_NAME_RE = re.compile(r'^/\S+/\S+/\S+$')


class DatasetMeta(type):
    """The metaclass for all datasets."""

    def __eq__(cls, other):
        return isinstance(other, DatasetMeta) and cls.name == other.name

    def __hash__(cls):
        return hash(cls.name)

    def _validate_name(cls):
        if not getattr(cls, 'name', None) or not DATASET_NAME_RE.match(cls.name):
            raise AttributeError(
                'The class attribute "name" must refer to a fully qualified dataset '
                'name of the form "/primary_dataset/processed_dataset/data_tier"'
            )

    @cached_class_property
    def dbs_dataset_record(cls):
        """The dataset's information registered with DBS."""
        cls._validate_name()
        return get_dataset_record_from_dbs(dataset=cls.name, instance=cls.dbs_instance)

    @cached_class_property
    def dbs_file_records(cls):
        """The dataset's file information registered with DBS."""
        cls._validate_name()
        return get_file_records_from_dbs(dataset=cls.name, instance=cls.dbs_instance)


class DatasetBase(object):
    """The base class for datasets."""

    __metaclass__ = DatasetMeta

    # The fully qualified dataset name of the format
    # "/primary_dataset/processed_dataset/data_tier".
    name = None

    # The DBS server instance where the dataset is registered.
    # This defaults to "global".
    dbs_instance = 'global'

    def __init__(self, selection=None, event_weight=None, chunk_size=2000, valid=True):
        """
        Parameters
        ----------
        selection : string, optional
        event_weight : string, optional
        chunk_size : numeric, optional
        valid : bool, optional
        """
        self.selection = selection
        self.event_weight = event_weight
        self.chunk_size = chunk_size
        self.valid = valid

    def __iter__(self):
        #try:
        #    files = self.files
        #except AttributeError:
        #    files = self.dbs_file_records
        pass
        

class MonteCarloBase(DatasetBase):
    """The base class for Monte Carlo samples."""

    # The cross section in units of picobarns (pb).
    cross_section = None


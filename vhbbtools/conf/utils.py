import collections

try:
    from dbs.apis.dbsClient import DbsApi
except ImportError:
    raise ImportError(
        "Couldn't import dbs. Has the environment been configured for CRAB3?"
    )


DBS_DATASET_FIELDS = (
    'acquisition_era_name',
    'create_by',
    'creation_date',
    'data_tier_name',
    'dataset',
    'dataset_access_type',
    'dataset_id',
    'last_modification_date',
    'last_modified_by',
    'physics_group_name',
    'prep_id',
    'primary_ds_name',
    'primary_ds_type',
    'processed_ds_name',
    'processing_version',
    'xtcrosssection',
)

DBS_FILE_FIELDS = (
    'adler32',
    'auto_cross_section',
    'block_id',
    'block_name',
    'branch_hash_id',
    'check_sum',
    'create_by',
    'creation_date',
    'dataset',
    'dataset_id',
    'event_count',
    'file_id',
    'file_size',
    'file_type',
    'file_type_id',
    'is_file_valid',
    'last_modification_date',
    'last_modified_by',
    'logical_file_name',
    'md5',
)


DatasetRecordBase = collections.namedtuple(typename='DatasetRecordBase', field_names=DBS_DATASET_FIELDS)


class DatasetRecord(DatasetRecordBase):
    """A namedtuple for DBS dataset records.

    Attribute access is available for the following information:
        * acquisition_era_name
        * create_by
        * creation_date
        * data_tier_name
        * dataset
        * dataset_access_type
        * dataset_id
        * last_modification_date
        * last_modified_by
        * physics_group_name
        * prep_id
        * primary_ds_name
        * primary_ds_type
        * processed_ds_name
        * processing_version
        * xtcrosssection
    """
    __slots__ = ()

    def __repr__(self):
        return 'DatasetRecord({0})'.format(', '.join('{0}={1!r}'.format(k, v) for k, v in self._asdict().iteritems()))


FileRecordBase = collections.namedtuple(typename='FileRecordBase', field_names=DBS_FILE_FIELDS)


class FileRecord(FileRecordBase):
    """A namedtuple for DBS file records.

    Attribute access is available for the following information:
        * adler32
        * auto_cross_section
        * block_id
        * block_name
        * branch_hash_id
        * check_sum
        * create_by
        * creation_date
        * dataset
        * dataset_id
        * event_count
        * file_id
        * file_size
        * file_type
        * file_type_id
        * is_file_valid
        * last_modification_date
        * last_modified_by
        * logical_file_name
        * md5
    """
    __slots__ = ()

    def __repr__(self):
        return 'FileRecord({0})'.format(', '.join('{0}={1!r}'.format(k, v) for k, v in self._asdict().iteritems()))


def get_dbs_api(instance='global'):
    """Return an API client for a CMS Dataset Bookkeeping (DBS) server instance.

    For a given DBS instance, a new DbsApi object is returned on the first call.
    Subsequent calls for the same DBS instance return the same DbsApi object to
    avoid reinitialization.

    Parameters
    ----------
    instance : str
        One of the following DBS server instances:
        * global (default)
        * phys01
        * phys02
        * phys03
        * caf

    Returns
    -------
    DbsApi
        A DbsApi object configured for the requested DBS server instance.
    """
    DBS_INSTANCES = {'global', 'phys01', 'phys02', 'phys03', 'caf'}
    if instance not in DBS_INSTANCES:
        raise ValueError('Unrecognized DBS instance: {0}'.format(instance))
    dbs_api = globals().get(instance.upper(), None)
    if dbs_api is None:
        url = 'https://cmsweb.cern.ch/dbs/prod/{0}/DBSReader'.format(instance)
        dbs_api = DbsApi(url)
        globals()[instance.upper()] = dbs_api
    return dbs_api


class DBSRecordNotFoundError(Exception):
    pass


def get_dataset_record_from_dbs(dataset, instance='global'):
    """Get a dataset record from DBS.

    Parameters
    ----------
    dataset : str
        A fully qualified dataset name in the format
        "/primary_dataset/processed_dataset/data_tier".
    instance : str, optional
        The DBS server instance where the dataset was published.
        This can be one of the following DBS server instances:
        * global (default)
        * phys01
        * phys02
        * phys03
        * caf

    Returns
    -------
    DatasetRecord
        A DatasetRecord namedtuple.
    """
    dbs_api = get_dbs_api(instance)
    json_data = dbs_api.listDatasets(dataset=dataset, detail=True)
    if json_data:
        dataset_record = DatasetRecord(**json_data[0])
        return dataset_record
    else:
        raise DBSRecordNotFoundError('Unable to locate dataset record for {0} from {1}'.format(dataset, dbs_api.url))


def get_file_records_from_dbs(dataset, instance='global'):
    """Get file records for a dataset from DBS.

    Parameters
    ----------
    dataset : str
        A fully qualified dataset name in the format
        "/primary_dataset/processed_dataset/data_tier".
    instance : str, optional
        The DBS server instance where the dataset was published.
        This can be one of the following DBS server instances:
        * global (default)
        * phys01
        * phys02
        * phys03
        * caf

    Returns
    -------
    list of FileRecords
        A list of FileRecord namedtuples for each file of the dataset,
        sorted lexicographically by "logical_file_name".
    """
    dbs_api = get_dbs_api(instance)
    json_data = dbs_api.listFiles(dataset=dataset, detail=True)
    if json_data:
        file_records = (FileRecord(**row) for row in json_data)
        return sorted(file_records, key=lambda record: record.logical_file_name)
    else:
        raise DBSRecordNotFoundError('Unable to locate file records for {0} from {1}'.format(dataset, dbs_api.url))


class cached_class_property(object):
    """A decorator that converts class methods into cached class properties.

    Parameters
    ----------
    func : method
        A method with a single cls argument.
    """
    def __init__(self, func):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        value = self.func(instance)
        setattr(instance, self.func.__name__, value)
        return value


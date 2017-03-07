from abc import ABCMeta, abstractmethod
from marshmallow.fields import List, String, UUID, Integer, Boolean, DateTime
from marshmallow.validate import ContainsOnly, NoneOf, OneOf
from marshmallow import (
    Schema, pre_load, pre_dump, post_load, validates_schema,
    validates, fields, ValidationError
)


class MemberExistsException(Exception):
    "Exception to specify that a setting member already exists"
    pass


class CollectionBase(metaclass=ABCMeta):
    "Base class for Collections, Nodes and Links"

    class _Schema(Schema):
        pass

    _key_field = None
    _allow_extra_fields = True
    _collection_config = {}

    @abstractmethod
    def __init__(self, collection_name):
        pass


class Collection(CollectionBase):

    __collection__ = None

    _safe_list = [
        '__collection__', '_safe_list', '_relations', '_id', '_index', '_collection_config'
    ]

    def __init__(self, collection_name=None, **kwargs):
        if collection_name is not None:
            self.__collection__ = collection_name

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        ret = "<" + self.__class__.__name__

        if hasattr(self, '_key'):
            ret += "(_key=" + getattr(self, '_key') + ')'

        ret += ">"

        return ret

    def __repr__(self):
        return self.__str__()

    @classmethod
    def _load(cls, in_dict):
        "Create object from given dict"
        data, errors = cls._Schema().load(in_dict)
        if errors:
            raise RuntimeError("Error loading object of collection {} - {}".format(
                cls.__name__, errors))

        new_obj = cls()

        for k, v in data.items():
            if k in cls._safe_list or (k in dir(cls) and callable(getattr(cls, k))):
                raise MemberExistsException(
                    "{} is already a member of {} instance and cannot be overwritten".format(
                        k, cls.__name__))

            setattr(new_obj, k, v)

        if '_key' in in_dict and not hasattr(new_obj, '_key'):
            setattr(new_obj, '_key', in_dict['_key'])

        if '_id' in in_dict:
            new_obj.__collection__ = in_dict['_id'].split('/')[0]

        return new_obj

    def _dump(self, **kwargs):
        "Dump all object attributes into a dict"

        data, errors = self._Schema(**kwargs).dump(self)
        if errors:
            raise RuntimeError("Error dumping object of collection {} - {}".format(
                self.__class__.__name__, errors))

        if '_key' not in data and hasattr(self, '_key'):
            data['_key'] = getattr(self, '_key')

        return data

    @property
    def _id(self):
        if hasattr(self, '_key') and getattr(self, '_key') is not None:
            return self.__collection__ + '/' + getattr(self, '_key')

        return None


class Relation(Collection):

    _safe_list = [
        '__collection__', '_safe_list', '_id', '_collections_from', '_collections_to',
        '_object_from', '_object_to', '_index', '_collection_config'
    ]

    def __init__(self, collection_name=None, **kwargs):

        if '_collections_from' in kwargs:
            self._collections_from = kwargs['_collections_from']
        else:
            self._collections_from = None

        if '_collections_to' in kwargs:
            self._collections_to = kwargs['_collections_to']
        else:
            self._collections_to = None

        self._from = None
        self._to = None
        self._object_from = None
        self._object_to = None

        super().__init__(collection_name=collection_name, **kwargs)

    def __str__(self):
        ret = "<" + self.__class__.__name__ + '('

        if hasattr(self, '_key'):
            ret += "_key=" + getattr(self, '_key')

        if hasattr(self, '_from') and hasattr(self, '_to'):
            ret += ", _from={}, _to={}".format(getattr(self, '_from'), getattr(self, '_to'))

        ret += ")>"

        return ret

    @classmethod
    def _load(cls, in_dict):
        "Create object from given dict"

        data, errors = cls._Schema().load(in_dict)
        if errors:
            raise RuntimeError("Error loading object of relation {} - {}".format(
                cls.__name__, errors))

        new_obj = cls()

        for k, v in data.items():
            if k in cls._safe_list or (k in dir(cls) and callable(getattr(cls, k))):
                raise MemberExistsException(
                    "{} is already a member of {} instance and cannot be overwritten".format(
                        k, cls.__name__))

            setattr(new_obj, k, v)

        if '_key' in in_dict and not hasattr(new_obj, '_key'):
            setattr(new_obj, '_key', in_dict['_key'])

        if '_id' in in_dict:
            new_obj.__collection__ = in_dict['_id'].split('/')[0]

        if '_from' in in_dict:
            setattr(new_obj, '_from', in_dict['_from'])

        if '_to' in in_dict:
            setattr(new_obj, '_to', in_dict['_to'])

        return new_obj

    def _dump(self, **kwargs):
        "Dump all object attributes into a dict"

        data = super()._dump(**kwargs)

        if '_from' not in data and hasattr(self, '_from'):
            data['_from'] = getattr(self, '_from')

        if '_to' not in data and hasattr(self, '_to'):
            data['_to'] = getattr(self, '_to')

        return data

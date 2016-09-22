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

    _safe_list = ['__collection__', '_safe_list']

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


class Node(Collection):

    pass


class Link(Collection):

    pass

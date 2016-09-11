from abc import ABCMeta, abstractmethod
from marshmallow.fields import List, String, UUID, Integer, Boolean, DateTime
from marshmallow.validate import ContainsOnly, NoneOf, OneOf
from marshmallow import (
    Schema, pre_load, pre_dump, post_load, validates_schema,
    validates, fields, ValidationError
)


class CollectionBase(metaclass=ABCMeta):
    "Base class for Collections, Nodes and Links"

    class _Schema(Schema):
        pass

    _key = None
    _allow_extra_fields = True
    _collection_config = {}

    @abstractmethod
    def __init__(self, collection_name):
        pass


class Collection(CollectionBase):

    __collection__ = None

    def __init__(self, collection_name=None):
        if collection_name is not None:
            self.__collection__ = collection_name


class Node(Collection):

    pass


class Link(Collection):

    pass

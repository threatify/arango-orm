"""
A wrapper around python-arango's database class adding some SQLAlchemy like ORM methods to it.
"""
from inspect import isclass

from arango.database import Database as ArangoDatabase
from .collections import CollectionBase
from .query import Query


class Database(ArangoDatabase):
    """
    Serves similar to SQLAlchemy's session object with the exception that it also allows
    creating and dropping collections etc.
    """

    def __init__(self, db):

        self._db = db
        super(Database, self).__init__(db._conn)

    def _verify_collection(self, col):
        "Verifies the give collection class or object of a collection class"

        if isclass(col):
            assert issubclass(col, CollectionBase)

        else:
            assert issubclass(col.__class__, CollectionBase)

        assert col.__collection__ is not None

    def create_collection(self, collection):
        "Create a collection"

        self._verify_collection(collection)

        super().create_collection(name=collection.__collection__,
                                  **collection._collection_config)

    def drop_collection(self, collection):
        "Drop a collection"
        self._verify_collection(collection)

        super().delete_collection(name=collection.__collection__)

    def add(self, entity):
        "Add a record to a collection"

        collection = self._db.collection(entity.__collection__)
        return collection.insert(entity._dump())

    def delete(self, entity, **kwargs):
        "Delete given document"

        collection = self._db.collection(entity.__collection__)
        return collection.delete(entity._dump(), **kwargs)

    def update(self, entity, **kwargs):
        "Update given document"

        collection = self._db.collection(entity.__collection__)
        return collection.update(entity._dump(), **kwargs)

    def query(self, CollectionClass):
        "Query given collection"

        return Query(CollectionClass, self)

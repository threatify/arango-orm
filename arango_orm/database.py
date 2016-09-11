"""
A wrapper around python-arango's database class adding some SQLAlchemy like ORM methods to it.
"""
from inspect import isclass

from arango.database import Database as ArangoDatabase
from .collections import CollectionBase


class Database(ArangoDatabase):
    """
    Serves similar to SQLAlchemy's session object with the exception that it also allows
    creating and dropping collections etc.
    """

    def __init__(self, db):

        self._db = db
        super(Database, self).__init__(db._conn)

    def create_all(self):
        """
        Create all collections, edges, graphs if they don't already exist
        """

        pass

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

    def add(self):
        "Add a record to a collection"

        pass

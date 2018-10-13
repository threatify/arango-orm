"""
Arango connection pooler.

Use multiple connections to access a database (usually database cluster) in
round robin fashion.
"""

import logging
from .database import Database  # pylint: disable=E0402

log = logging.getLogger(__name__)


class ConnectionPool(object):
    """Connection Pooler."""

    def __init__(self, connections, dbname, username, password):
        """Initialize connection pooler with ArangoClient connections."""
        self.pool = []
        self.conn_idx = 0
        assert connections
        for client in connections:
            d = client.db(dbname, username=username, password=password)
            self.pool.append(Database(d))

    @property
    def _db(self):
        """Return the next db object in pool."""
        curr_db = self.pool[self.conn_idx]
        self.conn_idx += 1
        if self.conn_idx >= len(self.pool):
            self.conn_idx = 0

        return curr_db

    @property
    def _conn(self):
        """Return the underlying ArangoClient connection."""
        return self._db._conn

    def _verify_collection(self, col):
        """Database._verify_collection wrapper."""
        self._db._verify_collection(col)

    def has_collection(self, collection):
        """Database.has_collection wrapper."""
        return self._db.has_collection(collection)

    def create_collection(self, collection, **col_args):
        """Database.create_collection wrapper."""
        self._db.create_collection(collection, **col_args)

    def drop_collection(self, collection):
        """Database.drop_collection wrapper."""
        self._db.drop_collection(collection)

    def has(self, collection, key):
        """Database.has wrapper."""
        return self._db.has(collection, key)

    def exists(self, document):
        """Database.exists wrapper."""
        return self._db.exists(document)

    def add(self, entity):
        """Database.add wrapper."""
        return self._db.add(entity)

    def delete(self, entity, **kwargs):
        """Database.delete wrapper."""
        return self._db.delete(entity, **kwargs)

    def update(self, entity, only_dirty=False, **kwargs):
        """Database.update wrapper."""
        return self._db.update(entity, only_dirty=only_dirty, **kwargs)

    def query(self, CollectionClass):
        """Database.query wrapper."""
        return self._db.query(CollectionClass)

    def create_graph(self, graph_object, **kwargs):
        """Database.create_graph wrapper."""
        self._db.create_graph(graph_object, **kwargs)

    def drop_graph(self, graph_object, drop_collections=True, **kwargs):
        """Database.drop_graph wrapper."""
        self._db.drop_graph(
            graph_object, drop_collections=drop_collections, **kwargs)

    def update_graph(self, graph_object, graph_info=None):
        """Database.update_graph wrapper."""
        self._db.update_graph(graph_object, graph_info=graph_info)

    def _is_same_edge(self, e1, e2):
        """Database._is_same_edge wrapper."""
        return self._db._is_same_edge(e1, e2)

    def _get_graph_info(self, graph_obj):
        """Database._get_graph_info wrapper."""
        return self._db._get_graph_info(graph_obj)

    def create_all(self, db_objects):
        """Database.create_all wrapper."""
        self._db.create_all(db_objects)

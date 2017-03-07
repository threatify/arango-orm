"""
A wrapper around python-arango's database class adding some SQLAlchemy like ORM methods to it.
"""
from copy import deepcopy
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
        "Verifies that col is a collection class or object of a collection class"

        if isclass(col):
            assert issubclass(col, CollectionBase)

        else:
            assert issubclass(col.__class__, CollectionBase)

        assert col.__collection__ is not None

    def create_collection(self, collection, **col_args):
        "Create a collection"

        self._verify_collection(collection)

        if hasattr(collection, '_collection_config'):
            col_args.update(collection._collection_config)

        col = super().create_collection(name=collection.__collection__, **col_args)

        if hasattr(collection, '_index'):
            for index in collection._index:
                index_create_method_name = 'add_{}_index'.format(index['type'])

                d = deepcopy(index)
                del d['type']

                # create the index
                getattr(col, index_create_method_name)(**d)

    def drop_collection(self, collection):
        "Drop a collection"
        self._verify_collection(collection)

        super().delete_collection(name=collection.__collection__)

    def has(self, collection, key):
        "Check if the document with given key exists in the given collection"

        return self._db.collection(collection.__collection__).has(key)

    def exists(self, document):
        "Similar to has but takes in a document object and searches using it's _key"

        return self._db.collection(document.__collection__).has(document._key)

    def add(self, entity):
        "Add a record to a collection"

        collection = self._db.collection(entity.__collection__)
        res = collection.insert(entity._dump())
        if not hasattr(entity, '_key') and '_key' in res:
            setattr(entity, '_key', res['_key'])

        return res

    def delete(self, entity, **kwargs):
        "Delete given document"

        collection = self._db.collection(entity.__collection__)
        return collection.delete(entity._dump(only=('_key', ))['_key'], **kwargs)

    def update(self, entity, **kwargs):
        "Update given document"

        collection = self._db.collection(entity.__collection__)
        return collection.update(entity._dump(), **kwargs)

    def query(self, CollectionClass):
        "Query given collection"

        return Query(CollectionClass, self)

    def create_graph(self, graph_object):
        "Create a named graph from given graph object"

        graph_edge_definitions = []

        # Create collections manually here so we also create indices
        # defined within the collection class. If we let the create_graph
        # call create the collections, it won't create the indices
        for _, col_obj in graph_object.vertices.items():
            self.create_collection(col_obj)

        for _, rel_obj in graph_object.edges.items():
            self.create_collection(rel_obj, edge=True)

        for _, relation_obj in graph_object.edges.items():

            cols_from = []
            cols_to = []

            if isinstance(relation_obj._collections_from, (list, tuple)):
                cols_from = relation_obj._collections_from
            else:
                cols_from = [relation_obj._collections_from, ]

            if isinstance(relation_obj._collections_to, (list, tuple)):
                cols_to = relation_obj._collections_to
            else:
                cols_to = [relation_obj._collections_to, ]

            from_col_names = [col.__collection__ for col in cols_from]
            to_col_names = [col.__collection__ for col in cols_to]

            graph_edge_definitions.append({
                'name': relation_obj.__collection__,
                'from_collections': from_col_names,
                'to_collections': to_col_names
            })

        self._db.create_graph(graph_object.__graph__, graph_edge_definitions)

    def drop_graph(self, graph_object, drop_collections=True):
        """
        Drop a graph, if drop_collections is True, drop all vertices and edges too
        """

        graph = self._db.graph(graph_object.__graph__)

        if drop_collections:
            for col in graph_object.edges:
                graph.delete_edge_definition(col, purge=True)

            for col in graph_object.vertices:
                graph.delete_vertex_collection(col, purge=True)

        self._db.delete_graph(graph_object.__graph__)

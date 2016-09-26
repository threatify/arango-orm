from inspect import isclass
from .collections import Relation


class GraphConnection(object):

    def __init__(self, collections_from, relation, collections_to):
        "Create a graph connection object"

        self.collections_from = collections_from
        self.collections_to = collections_to

        # Check if relation is an object of Relation class or a sub-class of Relation class
        # for the later, create an object
        relation_obj = None

        if isclass(relation):
            assert issubclass(relation, Relation)
            relation_obj = relation()
        else:
            relation_obj = relation

        relation_obj._collections_from = collections_from
        relation_obj._collections_to = collections_to

        self.relation = relation_obj


class Graph(object):

    __graph__ = None
    graph_connections = None

    def __init__(self, graph_name=None, graph_connections=None):

        self.vertices = {}
        self.edges = {}

        if graph_name is not None:
            self.__graph__ = graph_name

        if graph_connections:
            self.graph_connections = graph_connections

        if self.graph_connections:
            for gc in self.graph_connections:

                froms = gc.collections_from
                if not isinstance(froms, (list, tuple)):
                    froms = [froms, ]

                tos = gc.collections_to
                if not isinstance(tos, (list, tuple)):
                    tos = [tos, ]

                # Note: self.vertices stores collection classes while self.relations stores
                # relation objects (not classes)
                for col in froms + tos:
                    if col.__collection__ not in self.vertices:
                        self.vertices[col.__collection__] = col

                if gc.relation.__collection__ not in self.edges:
                    self.edges[gc.relation.__collection__] = gc.relation

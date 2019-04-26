from inspect import isclass
from .collections import Relation, Collection, CollectionMeta
# import pdb


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

    def __str__(self):
        ret = "<{}(collections_from={}, relation={}, collections_to={})>".format(
            self.__class__.__name__,
            str(self.collections_from),
            str(self.relation),
            str(self.collections_to)
        )

        return ret

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        """
        Convert the GraphConnection relation to dict understandable by the underlying
        python-arango driver
        """

        cols_from = []
        cols_to = []

        if isinstance(self.collections_from, (list, tuple)):
            cols_from = self.collections_from
        else:
            cols_from = [self.collections_from, ]

        if isinstance(self.collections_to, (list, tuple)):
            cols_to = self.collections_to
        else:
            cols_to = [self.collections_to, ]

        from_col_names = [col.__collection__ for col in cols_from]
        to_col_names = [col.__collection__ for col in cols_to]

        return {
            'name': self.relation.__collection__,
            'from_collections': from_col_names,
            'to_collections': to_col_names
        }


class Graph(object):

    __graph__ = None
    graph_connections = None

    def __init__(self,
                 graph_name=None, graph_connections=None, connection=None):

        self.vertices = {}
        self.edges = {}
        self._db = connection
        self._graph = None

        if graph_name is not None:
            self.__graph__ = graph_name

        if self._db is not None:
            self._graph = self._db.graph(self.__graph__)

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

    def relation(self, relation_from, relation, relation_to):
        """
        Return relation (edge) object from given collection (relation_from and
        relation_to) and edge/relation (relation) objects
        """

        # relation._from = relation_from.__collection__ + '/' + relation_from._key
        # relation._to = relation_to.__collection__ + '/' + relation_to._key
        relation._from = relation_from._id
        relation._to = relation_to._id

        return relation

    def _doc_from_dict(self, doc_dict):
        "Given a result dictionary, creates and returns a document object"

        col_name = doc_dict['_id'].split('/')[0]
        CollectionClass = self.vertices[col_name]

        # remove empty values
        keys_to_del = []
        for k, v in doc_dict.items():
            if doc_dict[k] is None:
                keys_to_del.append(k)

        if keys_to_del:
            for k in keys_to_del:
                del doc_dict[k]

        return CollectionClass._load(doc_dict)

    def _objectify_results(self, results, doc_obj=None):
        """
        Make traversal results object oriented by adding all links to the first
        object's _relations attribute. If doc_obj is not provided, the first
        vertex of the first path is used.
        """

        # Create objects from vertices dicts
        documents = {}
        if doc_obj:
            documents[doc_obj._id] = doc_obj

        relations_added = {}

        for p_dict in results:

            for v_dict in p_dict['vertices']:
                if doc_obj is None:
                    # Get the first vertex of the first result, it's the parent object
                    doc_obj = self._doc_from_dict(v_dict)
                    documents[doc_obj._id] = doc_obj

                if v_dict['_id'] in documents:
                    continue

                # Get ORM class for the collection
                documents[v_dict['_id']] = self._doc_from_dict(v_dict)

            # Process each path as a unit
            # First edge's _from always points to our parent document
            parent_id = doc_obj._id

            for e_dict in p_dict['edges']:

                col_name = e_dict['_id'].split('/')[0]
                rel_identifier = parent_id + '->' + e_dict['_id']

                if rel_identifier in relations_added:
                    rel = relations_added[rel_identifier]

                else:
                    RelationClass = self.edges[col_name].__class__
                    rel = RelationClass._load(e_dict)
                    rel._object_from = documents[rel._from]
                    rel._object_to = documents[rel._to]

                    parent_object = None
                    if rel._from == parent_id:
                        parent_object = documents[rel._from]
                        rel._next = rel._object_to

                    elif rel._to == parent_id:
                        parent_object = documents[rel._to]
                        rel._next = rel._object_from

                    assert parent_object is not None

                    if not hasattr(parent_object, '_relations'):
                        setattr(parent_object, '_relations', {})

                    if col_name not in parent_object._relations:
                        parent_object._relations[col_name] = []

                    if rel not in parent_object._relations[col_name]:
                        parent_object._relations[col_name].append(rel)

                    if rel._id not in relations_added:
                        relations_added[rel_identifier] = rel

                # Set parent ID
                if rel._from == parent_id:
                    parent_id = rel._to

                elif rel._to == parent_id:
                    parent_id = rel._from

        return doc_obj

    def expand(self, doc_obj, direction='any', depth=1, only=None):
        """
        Graph traversal.

        Expand all links of given direction (outbound, inbound, any) upto given
        length for the given document object and update the object with the
        found relations.

        :param only: If given should be a string, Collection class or list of
        strings or collection classes containing target collection names of
        documents (vertices) that should be fetched.
        Any vertices found in traversal that don't belong to the specified
        collection names given in this parameter will be ignored.
        """
        assert direction in ('any', 'inbound', 'outbound')

        graph = self._db.graph(self.__graph__)
        doc_id = doc_obj._id
        doc_obj._relations = {}  # clear any previous relations
        filter_func = None
        if only:
            if not isinstance(only, (list, tuple)):
                only = [only, ]

            c_str = ""
            for c in only:
                if not isinstance(c, str) and hasattr(c, '__collection__'):
                    c = c.__collection__

                c_str += "vertex._id.match(/" + c + r"\/.*/) ||"

            if c_str:
                c_str = c_str[:-3]

            filter_func = """
                if ({condition})
                    {{ return; }}
                return 'exclude';
            """.format(
                condition=c_str
            )

        results = graph.traverse(
            start_vertex=doc_id,
            direction=direction,
            vertex_uniqueness='path',
            min_depth=1, max_depth=depth,
            filter_func=filter_func
        )

        self._objectify_results(results['paths'], doc_obj)

    def aql(self, query, **kwargs):
        """Run AQL graph traversal query."""
        results = self._db.aql.execute(query, **kwargs)

        doc_obj = self._objectify_results(results)

        return doc_obj

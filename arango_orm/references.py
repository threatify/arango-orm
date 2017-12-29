from pydoc import locate


class Relationship(object):

    def __init__(self, col_class, field, **kwargs):

        # target_field='_key', uselist=True, order_by=None
        self._col_class = col_class
        self.field = field
        self.target_field = kwargs.get('target_field', '_key')
        self.uselist = kwargs['uselist']
        self.order_by = kwargs.get('order_by', None)
        self.cache = kwargs.get('cache', True)

    @property
    def col_class(self):

        from .collections import Collection, Relation

        if isinstance(self._col_class, str):
            self._col_class = locate(self._col_class)
            assert issubclass(self._col_class, (Collection, Relation))

        return self._col_class


class GraphRelationship(Relationship):
    pass


def relationship(col_class_or_name, field, **kwargs):
    """
    Define a relationship to another document of same or different collection and making
    that document available as an instance property of the class where relationship is
    created.

    :param col_class_or_name: Collection class or fully qualified name string of the class
    :param field: The local field's name used for the linkage
    :param target_field: Default '_key'. The field in the target collection to match to
    :param uselist:
        Default None. If not specified then this parameter is determined automatically
        based on whether we are linking to the _key field in which case uselist is False.
        When linking to fields other than _key, this parameter is set to True.
    :param order_by: Default None. Not implemented yet. Will be used to sort linked documents
    :param cache:
        Default True. Cache fetched documents so future access does not require querying
        the database.
    """

    # target_field='_key', uselist=None, order_by=None
    target_field = kwargs.get('target_field', '_key')
    uselist = kwargs.get('uselist', None)
    order_by = kwargs.get('order_by', None)
    cache = kwargs.get('cache', True)

    if uselist is None:
        if '_key' == target_field:
            uselist = False
        else:
            uselist = True

    p_dict = dict(target_field=target_field, uselist=uselist, cache=cache, order_by=order_by)

    return Relationship(col_class_or_name, field, **p_dict)


def graph_relationship(col_class_or_name, field, **kwargs):
    pass

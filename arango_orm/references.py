from pydoc import locate


class Relationship(object):

    def __init__(self, col_class, field, target_field='_key', uselist=True, order_by=None):

        self._col_class = col_class
        self.field = field
        self.target_field = target_field
        self.uselist = uselist
        self.order_by = order_by

    @property
    def col_class(self):

        from .collections import Collection, Relation

        if isinstance(self._col_class, str):
            self._col_class = locate(self._col_class)
            assert issubclass(self._col_class, (Collection, Relation))

        return self._col_class


class GraphRelationship(Relationship):
    pass


def relationship(col_class_or_name, field, target_field='_key', uselist=None, order_by=None):


    if uselist is None:
        if '_key' == target_field:
            uselist = False
        else:
            uselist = True

    return Relationship(col_class_or_name, field, target_field, uselist, order_by)


def graph_relationship(col_class_or_name, field, target_field='_key', uselist=None, order_by=None):
    pass

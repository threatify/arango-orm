

class Relationship(object):

    def __init__(self, col_class, field, target_field='_key', uselist=True, order_by=None):

        self.col_class = col_class
        self.field = field
        self.target_field = target_field
        self.uselist = uselist
        self.order_by = order_by


class GraphRelationship(Relationship):
    pass


def relationship(col_class_or_name, field, target_field='_key', uselist=None, order_by=None):

    # TODO: if col_class_or_name is string, resolve to class
    if uselist is None:
        if '_key' == target_field:
            uselist = False
        else:
            uselist = True

    return Relationship(col_class_or_name, field, target_field, uselist, order_by)


def graph_relationship(col_class_or_name, field, target_field='_key', uselist=None, order_by=None):
    pass

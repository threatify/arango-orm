class lazy_property(object):
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, instance, cls):
        value = self.fget(instance)
        setattr(instance, self.fget.__name__, value)
        return value

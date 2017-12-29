from datetime import datetime
from arango import ArangoClient
from arango_orm.database import Database

from arango_orm.fields import String, Date, Integer, Boolean
from arango_orm import Collection, Relation, Graph, GraphConnection
from arango_orm.references import relationship, graph_relationship


class lazy_property(object):
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, instance, cls):
        value = self.fget(instance)
        setattr(instance, self.fget.__name__, value)
        return value


class Person(Collection):

    __collection__ = 'persons'
    _allow_extra_fields = False
    _index = [{'type': 'hash', 'unique': False, 'fields': ['name']}]
    _allow_extra_fields = False  # prevent extra properties from saving into DB

    _key = String(required=True)
    name = String(required=True, allow_none=False)
    age = Integer(missing=None)
    dob = Date()
    is_staff = Boolean(default=False)

    cars = relationship(__name__ + ".Car", '_key', target_field='owner_key')

    @property
    def is_adult(self):
        return self.age and self.age >= 18

    @lazy_property
    def lazy_is_adult(self):
        return self.age and self.age >= 18

    def __str__(self):
        return "<Person(" + self.name + ")>"


class Car(Collection):

    __collection__ = 'cars'
    _allow_extra_fields = True

    make = String(required=True)
    model = String(required=True)
    year = Integer(required=True)
    owner_key = String()

    owner = relationship(Person, 'owner_key', cache=False)

    def __str__(self):
        return "<Car({} - {} - {})>".format(self.make, self.model, self.year)



client = ArangoClient(username='test', password='test')
db = Database(client.db('test'))

p = Person(_key='kashif', name='Kashif Iftikhar', dob=datetime.today())
db.add(p)
p2 = Person(_key='azeen', name='Azeen Kashif', dob=datetime.today())
db.add(p2)

c1 = Car(make='Honda', model='Civic', year=1984, owner_key='kashif')
db.add(c1)

c2 = Car(make='Mitsubishi', model='Lancer', year=2005, owner_key='kashif')
db.add(c2)

c3 = Car(make='Acme', model='Toy Racer', year=2016, owner_key='azeen')
db.add(c3)


c3 = db.query(Car).filter_by(make='Acme').first()

print(c1.owner)
print(c1.owner.name)
print(c2.owner.name)
print(c3.owner.name)

print(p.cars)
print(p.cars[0].make)

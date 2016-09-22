from marshmallow import Schema
from marshmallow.fields import String, Date, Integer
from arango_orm.collections import Collection


class Person(Collection):

    __collection__ = 'persons'

    class _Schema(Schema):
        _key = String(required=True)
        name = String(required=True, allow_none=False)
        dob = Date()


class Car(Collection):

    __collection__ = 'cars'

    class _Schema(Schema):

        make = String(required=True)
        model = String(required=True)
        year = Integer(required=True)


cars = [
    Car(make="Honda", model="Civic", year=1984),
    Car(make="Honda", model="Civic", year=1995),
    Car(make="Honda", model="Civic", year=1998),
    Car(make="Honda", model="Civic", year=2001),
    Car(make="Toyota", model="Corolla", year=1988),
    Car(make="Toyota", model="Corolla", year=2004),
    Car(make="Mitsubishi", model="Lancer", year=2005)
]

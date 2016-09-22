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

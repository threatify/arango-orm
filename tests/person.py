from marshmallow import Schema
from marshmallow.fields import String, Date
from arango_orm.collections import Collection


class Person(Collection):
    __collection__ = 'persons'

    class _Schema(Schema):
        cnic = String(required=True)
        name = String(required=True, allow_none=False)
        dob = Date()

    _key_field = 'cnic'

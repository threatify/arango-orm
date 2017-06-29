from arango import ArangoClient
from arango_orm.database import Database
from arango_orm.collections import Collection
from marshmallow.fields import List, String, UUID, Integer, Boolean, DateTime, Date
from marshmallow import (
    Schema, pre_load, pre_dump, post_load, validates_schema,
    validates, fields, ValidationError
)

client = ArangoClient(username='test', password='test')
test_db = client.db('test')

db = Database(test_db)

class Setting(Collection):
    __collection__ = 'settings'

    # will have an extra field named value

    class _Schema(Schema):
        _key = String(required=True)


s = db.query(Setting).by_key('project_name')
s._dump()

s1 = Setting(_key='project_name', value='abc')
s1.value
s1._dump()

db.add(s1)

db.add(Setting(_key='boolean', value=True))
db.add(Setting(_key='integer', value=100))
db.add(Setting(_key='float', value=12.22))
db.add(Setting(_key='list', value=[1,2,3]))
db.add(Setting(_key='dict', value={'a': 1, 'b': 2}))

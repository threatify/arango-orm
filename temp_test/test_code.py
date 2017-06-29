from arango import ArangoClient
from arango_orm.database import Database
from arango_orm.collections import Collection
from tests.data import (UniversityGraph, Student, Teacher, Subject, SpecializesIn, Area,
                   teachers_data, students_data, subjects_data, specializations_data, areas_data)

client = ArangoClient(username='test', password='test')
test_db = client.db('test')

db = Database(test_db)

uni_graph = UniversityGraph(connection=db)

obj = uni_graph.aql("FOR v, e, p IN 1..2 INBOUND 'areas/Gotham' GRAPH 'university_graph'  RETURN p")

bruce = db.query(Teacher).by_key("T001")
amanda = db.query(Teacher).by_key("T003")

traversal_results = db.graph('university_graph').traverse(start_vertex='teachers/T001', direction='any',
                                       vertex_uniqueness='path', min_depth=1, max_depth=1)

uni_graph.expand(amanda, depth=3)

uni_graph.expand(bruce, depth=2)

bruce._relations['specializes_in'][0]._object_to._relations['teaches'][0]._object_from.name
bruce._relations['specializes_in'][0]._next._relations['teaches'][0]._next.name


###############################3
from datetime import date
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



from tests.data import Person, Car, cars

db.query(Car).filter("model==@model", model='Civic').update(model='CIVIC', make='HONDA')

lancer = Car(make='Mitsubishi', model='Lancer', year=2005)
db.add(lancer)
lancer._dump()

class Person(Collection):
    __collection__ = 'persons'

    class _Schema(Schema):
        _key = String(required=True)
        name = String(required=True, allow_none=False)
        dob = Date()



db.query(Person).count()
db.query(Person).all()

p = Person(name='test', _key='12312', dob=date(year=2016, month=9, day=12))
db.add(p)
db.query(Person).count()


pd = {'_key': '37405-4564665-7', 'dob': '2016-09-12', 'name': 'Kashif Iftikhar'}
data, errors = Person._Schema().load(pd)
new_person = Person._load(pd)

new_col = Collection('new_collection')
db.create_collection(new_col)
db.drop_collection(new_col)

# db._query(` FOR v, e, p IN 1..1 ANY 'teachers/T001' GRAPH 'university_graph' FILTER LIKE(p.edges[0]._id, 'resides_in%')  RETURN p`);
# db._query(` FOR v, e, p IN 2..2 ANY 'teachers/T001' GRAPH 'university_graph' FILTER LIKE(p.edges[0]._id, 'resides_in%')  RETURN p`);

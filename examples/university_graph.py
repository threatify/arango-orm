import sys
from arango_orm.fields import List, String, UUID, Integer, Boolean, DateTime
from marshmallow.validate import ContainsOnly, NoneOf, OneOf
from marshmallow import (
    Schema, pre_load, pre_dump, post_load, validates_schema,
    validates, fields, ValidationError
)

from arango import ArangoClient
from arango_orm.database import Database

from arango_orm.collections import Collection, Relation
from arango_orm.graph import Graph, GraphConnection

from pprint import pprint as pp

class Student(Collection):
    __collection__ = 'students'

    class _Schema(Schema):
        _key = String(required=True)  # registration number
        name = String(required=True, allow_none=False)
        age = Integer()

    def __str__(self):
        return "<Student({},{})>".format(self._key, self.name)


class Teacher(Collection):
    __collection__ = 'teachers'

    class _Schema(Schema):
        _key = String(required=True)  # employee id
        name = String(required=True)

    def __str__(self):
        return "<Teacher({})>".format(self.name)


class Subject(Collection):
    __collection__ = 'subjects'

    class _Schema(Schema):
        _key = String(required=True)  # subject code
        name = String(required=True)
        credit_hours = Integer()
        has_labs = Boolean(missing=True)

    def __str__(self):
        return "<Subject({})>".format(self.name)


class Area(Collection):
    __collection__ = 'areas'

    class _Schema(Schema):
        _key = String(required=True)  # area name


class SpecializesIn(Relation):
    __collection__ = 'specializes_in'

    class _Schema(Schema):
        expertise_level = String(required=True, options=["expert", "medium", "basic"])
        _key = String(required=True)

    def __str__(self):
        return "<SpecializesIn(_key={}, expertise_level={}, _from={}, _to={})>".format(
            self._key, self.expertise_level, self._from, self._to)


class UniversityGraph(Graph):
    __graph__ = 'university_graph'

    graph_connections = [
        # Using general Relation class for relationship
        GraphConnection(Student, Relation("studies"), Subject),
        GraphConnection(Teacher, Relation("teaches"), Subject),
        GraphConnection(Teacher, Relation("teacher"), Student),

        # Using specific classes for vertex and edges
        GraphConnection(Teacher, SpecializesIn, Subject),
        GraphConnection([Teacher, Student], Relation("resides_in"), Area)

    ]

students_data = [
    Student(_key='S1001', name='John Wayne', age=30),
    Student(_key='S1002', name='Lilly Parker', age=22),
    Student(_key='S1003', name='Cassandra Nix', age=25),
    Student(_key='S1004', name='Peter Parker', age=20)
]

teachers_data = [
    Teacher(_key='T001', name='Bruce Wayne'),
    Teacher(_key='T002', name='Barry Allen'),
    Teacher(_key='T003', name='Amanda Waller')
]

subjects_data = [
    Subject(_key='ITP101', name='Introduction to Programming', credit_hours=4, has_labs=True),
    Subject(_key='CS102', name='Computer History', credit_hours=3, has_labs=False),
    Subject(_key='CSOOP02', name='Object Oriented Programming', credit_hours=3, has_labs=True),
]

specializations_data = [
    SpecializesIn(_from="teachers/T001", _to="subjects", expertise_level="medium")
]

areas_data = [
    Area(_key="Gotham"),
    Area(_key="Metropolis"),
    Area(_key="StarCity")
]

def data_create():
    for s in students_data:
        db.add(s)

    for t in teachers_data:
        db.add(t)

    for s in subjects_data:
        db.add(s)

    for a in areas_data:
        db.add(a)

    gotham = db.query(Area).by_key("Gotham")
    metropolis = db.query(Area).by_key("Metropolis")
    star_city = db.query(Area).by_key("StarCity")

    john_wayne = db.query(Student).by_key("S1001")
    lilly_parker = db.query(Student).by_key("S1002")
    cassandra_nix = db.query(Student).by_key("S1003")
    peter_parker = db.query(Student).by_key("S1004")

    intro_to_prog = db.query(Subject).by_key("ITP101")
    comp_history = db.query(Subject).by_key("CS102")
    oop = db.query(Subject).by_key("CSOOP02")

    barry_allen = db.query(Teacher).by_key("T002")
    bruce_wayne = db.query(Teacher).by_key("T001")
    amanda_waller = db.query(Teacher).by_key("T003")

    db.add(uni_graph.relation(peter_parker, Relation("studies"), oop))
    db.add(uni_graph.relation(peter_parker, Relation("studies"), intro_to_prog))
    db.add(uni_graph.relation(john_wayne, Relation("studies"), oop))
    db.add(uni_graph.relation(john_wayne, Relation("studies"), comp_history))
    db.add(uni_graph.relation(lilly_parker, Relation("studies"), intro_to_prog))
    db.add(uni_graph.relation(lilly_parker, Relation("studies"), comp_history))
    db.add(uni_graph.relation(cassandra_nix, Relation("studies"), oop))
    db.add(uni_graph.relation(cassandra_nix, Relation("studies"), intro_to_prog))

    db.add(uni_graph.relation(barry_allen, SpecializesIn(expertise_level="expert"), oop))
    db.add(uni_graph.relation(barry_allen, SpecializesIn(expertise_level="expert"), intro_to_prog))
    db.add(uni_graph.relation(bruce_wayne, SpecializesIn(expertise_level="medium"), oop))
    db.add(uni_graph.relation(bruce_wayne, SpecializesIn(expertise_level="expert"), comp_history))
    db.add(uni_graph.relation(amanda_waller, SpecializesIn(expertise_level="basic"), intro_to_prog))
    db.add(uni_graph.relation(amanda_waller, SpecializesIn(expertise_level="medium"), comp_history))

    db.add(uni_graph.relation(bruce_wayne, Relation("teacher"), peter_parker))
    db.add(uni_graph.relation(bruce_wayne, Relation("teacher"), john_wayne))
    db.add(uni_graph.relation(bruce_wayne, Relation("teacher"), lilly_parker))

    db.add(uni_graph.relation(bruce_wayne, Relation("teaches"), oop))
    db.add(uni_graph.relation(barry_allen, Relation("teaches"), intro_to_prog))
    db.add(uni_graph.relation(amanda_waller, Relation("teaches"), comp_history))

    db.add(uni_graph.relation(bruce_wayne, Relation("resides_in"), gotham))
    db.add(uni_graph.relation(barry_allen, Relation("resides_in"), star_city))
    db.add(uni_graph.relation(amanda_waller, Relation("resides_in"), metropolis))
    db.add(uni_graph.relation(john_wayne, Relation("resides_in"), gotham))
    db.add(uni_graph.relation(lilly_parker, Relation("resides_in"), metropolis))
    db.add(uni_graph.relation(cassandra_nix, Relation("resides_in"), star_city))
    db.add(uni_graph.relation(peter_parker, Relation("resides_in"), metropolis))


if '__main__' == __name__:
    usage = """
Usage: {} action

Supported actions are:

test_data_create - Create the test Data in Database
create_graph - Create the graph and all it's vertices and edges
drop_graph - Drop the graph and all it's vertices and edges
delete_database - delete test database
""".format(sys.argv[0])

    db_name = 'db_test'
    username = 'root'
    password = ''

    client = ArangoClient()
    test_db = client.db(db_name, username=username, password=password)

    db = Database(test_db)

    uni_graph = UniversityGraph(connection=db)

    if len(sys.argv) > 1:
        if 'test_data_create' == sys.argv[1]:
            db.create_graph(uni_graph)
            data_create()
        elif 'drop_graph' == sys.argv[1]:
            db.drop_graph(uni_graph)
        elif 'delete_database' == sys.argv[1]:
            client.delete_database(name=db_name)
    else:
        print(usage)

        bruce = db.query(Teacher).by_key("T001")
        uni_graph.expand(bruce, depth=1, direction='any')

        print('bruce._relations')
        pp(bruce._relations)

        students_of_bruce = [r._next for r in bruce._relations['teacher']]
        print('Students of Bruce')
        for s in students_of_bruce:
            pp(s)

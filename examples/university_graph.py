import sys
from marshmallow.fields import List, String, UUID, Integer, Boolean, DateTime
from marshmallow.validate import ContainsOnly, NoneOf, OneOf
from marshmallow import (
    Schema, pre_load, pre_dump, post_load, validates_schema,
    validates, fields, ValidationError
)

from arango import ArangoClient
from arango_orm.database import Database

from arango_orm.collections import Collection, Relation
from arango_orm.graph import Graph, GraphConnection


class Student(Collection):

    __collection__ = 'students'

    class _Schema(Schema):
        _key = String(required=True)  # registration number
        name = String(required=True, allow_none=False)
        age = Integer()


class Teacher(Collection):

    __collection__ = 'teachers'

    class _Schema(Schema):
        _key = String(required=True)  # employee id
        name = String(required=True)


class Subject(Collection):

    __collection__ = 'subjects'

    class _Schema(Schema):
        _key = String(required=True)  # subject code
        name = String(required=True)
        credit_hours = Integer()
        has_labs = Boolean(missing=True)


class SpecializesIn(Relation):

    __collection__ = 'specializes_in'

    class _Schema(Schema):
        expertise_level = String(options=["expert", "medium", "basic"])


class Area(Collection):

    __collection__ = 'areas'

    class _Schema(Schema):
        name = String(required=True)


class UniversityGraph(Graph):

    __graph__ = 'university_graph'

    graph_connections = [
        # Using general Relation class for relationship
        GraphConnection(Student, Relation("studies"), Subject),
        GraphConnection(Teacher, Relation("teaches"), Subject),

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

if '__main__' == __name__:

    usage = """
Usage: {} action

Supported actions are:

create_graph - Create the graph and all it's vertices and edges
drop_graph - Drop the graph and all it's vertices and edges
""".format(sys.argv[0])

    uni_graph = UniversityGraph()
    client = ArangoClient(username='test', password='test')
    test_db = client.db('test')

    db = Database(test_db)

    if len(sys.argv) > 1:
        if 'create_graph' == sys.argv[1]:
            db.create_graph(uni_graph)

        elif 'drop_graph' == sys.argv[1]:
            db.drop_graph(uni_graph)

    else:

        print(usage)

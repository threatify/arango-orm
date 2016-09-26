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
        expertise_level = String(options=["expert", "intermediate", "basic"])


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


if '__main__' == __name__:

    uni_graph = UniversityGraph()
    client = ArangoClient(username='test', password='test')
    test_db = client.db('test')

    db = Database(test_db)
    db.create_graph(uni_graph)

from marshmallow.fields import List, String, UUID, Integer, Boolean, DateTime
from marshmallow.validate import ContainsOnly, NoneOf, OneOf
from marshmallow import (
    Schema, pre_load, pre_dump, post_load, validates_schema,
    validates, fields, ValidationError
)

class NodeBase(object):
    pass

class Node(NodeBase):
    pass


class Link(NodeBase):
    pass


class GraphConnection(object):
    pass


class Graph(object):
    pass


class Student(Node):

    __collection__ = 'students'

    class _Schema(Schema):
        registration_number = String(required=True)
        name = String(required=True, allow_none=False)
        age = Integer()

    _key = _Schema.registration_number


class Teacher(Node):

    __collection__ = 'teachers'

    class _Schema(Schema):
        employee_id = String(required=True)
        name = String(required=True)

    _key = _Schema.employee_id


class Subject(Node):

    __collection__ = 'subjects'

    class _Schema(Schema):
        code = String(required=True)
        name = String(required=True)
        credit_hours = Integer()
        has_labs = Boolean(missing=True)

    _key = _Schema.code


class SpecializesIn(Link):

    __collection__ = 'specializes_in'

    class _Schema(Schema):
        expertise_level = String(options=["expert", "intermediate", "basic"])


class UniversityGraph(Graph):

    __graph__ = 'university_graph'
    graph = [
        # Using generic classes
        GraphConnection(Student, Link("has"), Node("address")),
        GraphConnection(Node("address"), Link("belongs_to"), Node("city")),
        GraphConnection(Node("city"), Link("belongs_to"), Node("country")),
        # Using general Link class for relationship
        GraphConnection(Student, Link("studies"), Subject),
        GraphConnection(Teacher, Link("teaches"), Subject),

        # Using specific classes for vertex and edges
        GraphConnection(Teacher, SpecializesIn, Subject),

    ]

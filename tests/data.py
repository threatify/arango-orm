from marshmallow import Schema
from marshmallow.fields import String, Date, Integer, Boolean
from arango_orm import Collection, Relation, Graph, GraphConnection


class Person(Collection):

    __collection__ = 'persons'
    _index = [{'type': 'hash', 'unique': False, 'fields': ['name']}]

    class _Schema(Schema):
        _key = String(required=True)
        name = String(required=True, allow_none=False)
        dob = Date()

    def __str__(self):
        return "<Person(" + self.name + ")>"


class Car(Collection):

    __collection__ = 'cars'

    class _Schema(Schema):

        make = String(required=True)
        model = String(required=True)
        year = Integer(required=True)

    def __str__(self):
        return "<Car({} - {} - {})>".format(self.make, self.model, self.year)

cars = [
    Car(make="Honda", model="Civic", year=1984),
    Car(make="Honda", model="Civic", year=1995),
    Car(make="Honda", model="Civic", year=1998),
    Car(make="Honda", model="Civic", year=2001),
    Car(make="Toyota", model="Corolla", year=1988),
    Car(make="Toyota", model="Corolla", year=2004),
    Car(make="Mitsubishi", model="Lancer", year=2005)
]


# Graph data
class Student(Collection):

    __collection__ = 'students'

    class _Schema(Schema):
        _key = String(required=True)  # registration number
        name = String(required=True, allow_none=False)
        age = Integer()

    def __str__(self):
        return "<Student({})>".format(self.name)


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


class SpecializesIn(Relation):

    __collection__ = 'specializes_in'

    class _Schema(Schema):
        expertise_level = String(required=True, options=["expert", "medium", "basic"])

    def __str__(self):
        return "<SpecializesIn(_key={}, expertise_level={}, _from={}, _to={})>".format(
            self._key, self.expertise_level, self._from, self._to)


class Area(Collection):

    __collection__ = 'areas'

    class _Schema(Schema):
        _key = String(required=True)  # area name


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

areas_data = [
    Area(_key="Gotham"),
    Area(_key="Metropolis"),
    Area(_key="StarCity")
]

specializations_data = [
    SpecializesIn(_from="teachers/T001", _to="subjects/ITP101", expertise_level="medium")
]


# FOR v, e, p IN 1..3 INBOUND 'areas/gotham'
# GRAPH 'university_graph'
# RETURN p

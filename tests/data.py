from datetime import datetime
from arango_orm.fields import String, Date, Integer, Boolean
from arango_orm import Collection, Relation, Graph, GraphConnection
from arango_orm.references import relationship, graph_relationship

from .utils import lazy_property


class Person(Collection):

    __collection__ = 'persons'
    _allow_extra_fields = False
    _index = [{'type': 'hash', 'unique': False, 'fields': ['name']}]
    _allow_extra_fields = False  # prevent extra properties from saving into DB

    _key = String(required=True)
    name = String(required=True, allow_none=False)
    age = Integer(missing=None)
    dob = Date()
    is_staff = Boolean(default=False)

    cars = relationship(__name__ + ".Car", '_key', target_field='owner_key')

    @property
    def is_adult(self):
        return self.age and self.age >= 18

    @lazy_property
    def lazy_is_adult(self):
        return self.age and self.age >= 18

    def __str__(self):
        return "<Person(" + self.name + ")>"


class Car(Collection):

    __collection__ = 'cars'
    _allow_extra_fields = True

    make = String(required=True)
    model = String(required=True)
    year = Integer(required=True)
    owner_key = String()

    owner = relationship(Person, 'owner_key')

    def __str__(self):
        return "<Car({} - {} - {})>".format(self.make, self.model, self.year)

persons = [
    Person(_key='kashif', name='Kashif Iftikhar', dob=datetime.today()),
    Person(_key='azeen', name='Azeen Kashif', dob=datetime.today())
]
cars = [
    Car(make="Honda", model="Civic", year=1984, owner_key='kashif'),
    Car(make="Honda", model="Civic", year=1995, owner_key='kashif'),
    Car(make="Honda", model="Civic", year=1998, owner_key='Azeen'),
    Car(make="Honda", model="Civic", year=2001, owner_key='Azeen'),
    Car(make="Toyota", model="Corolla", year=1988, owner_key='kashif'),
    Car(make="Toyota", model="Corolla", year=2004, owner_key='Azeen'),
    Car(make="Mitsubishi", model="Lancer", year=2005, owner_key='Azeen')
]


# Graph data
class Student(Collection):

    __collection__ = 'students'

    _key = String(required=True)  # registration number
    name = String(required=True, allow_none=False)
    age = Integer()

    def __str__(self):
        return "<Student({})>".format(self.name)


class Teacher(Collection):

    __collection__ = 'teachers'

    _key = String(required=True)  # employee id
    name = String(required=True)

    def __str__(self):
        return "<Teacher({})>".format(self.name)


class Subject(Collection):

    __collection__ = 'subjects'

    _key = String(required=True)  # subject code
    name = String(required=True)
    credit_hours = Integer()
    has_labs = Boolean(missing=True)

    def __str__(self):
        return "<Subject({})>".format(self.name)


class SpecializesIn(Relation):

    __collection__ = 'specializes_in'

    _key = String(required=True)
    expertise_level = String(required=True, options=["expert", "medium", "basic"])

    def __str__(self):
        return "<SpecializesIn(_key={}, expertise_level={}, _from={}, _to={})>".format(
            self._key, self.expertise_level, self._from, self._to)


class Area(Collection):

    __collection__ = 'areas'

    _key = String(required=True)  # area name


# DUMMY COLLECTIONS #


class DummyFromCol1(Collection):

    __collection__ = 'dummy_from_col_1'
    _allow_extra_fields = True

    _key = String(required=True)


class DummyFromCol2(Collection):

    __collection__ = 'dummy_from_col_2'

    _key = String(required=True)


class DummyRelation(Relation):

    __collection__ = 'dummy_relation'

    _key = String(required=True)
    _from = String()
    _to = String()


class DummyToCol1(Collection):

    __collection__ = 'dummy_to_col_1'

    _key = String(required=True)


class DummyToCol2(Collection):

    __collection__ = 'dummy_to_col_2'

    _key = String(required=True)


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

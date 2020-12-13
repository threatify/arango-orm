from datetime import datetime
from arango_orm.fields import String, Date, Integer, Boolean, List, Nested, Number, Float
from arango_orm import Collection, Relation, Graph, GraphConnection
from arango_orm.references import relationship, graph_relationship

from .utils import lazy_property


class Person(Collection):
    class Hobby(Collection):
        class Equipment(Collection):
            name = String(required=False, allow_none=True)
            price = Number(required=False, allow_none=True)

        name = String(required=False, allow_none=True)
        type = String(required=True, allow_none=False)
        equipment = List(Nested(Equipment.schema()), required=False, allow_none=True, default=None)

    __collection__ = "persons"
    _allow_extra_fields = False
    _index = [{"type": "hash", "unique": False, "fields": ["name"]}]
    _allow_extra_fields = False  # prevent extra properties from saving into DB

    _key = String()
    name = String(required=True, allow_none=False)
    age = Integer(allow_none=True, missing=None)
    dob = Date(allow_none=True, missing=None)
    is_staff = Boolean(default=False)
    favorite_hobby = Nested(Hobby.schema(), required=False, allow_none=True, default=None)
    hobby = List(Nested(Hobby.schema()), required=False, allow_none=True, default=None)
    cars = relationship(__name__ + ".Car", "_key", target_field="owner_key")

    @property
    def is_adult(self):
        return self.age and self.age >= 18

    @lazy_property
    def lazy_is_adult(self):
        return self.age and self.age >= 18

    def __str__(self):
        return "<Person(" + self.name + ")>"


class Car(Collection):
    __collection__ = "cars"
    _allow_extra_fields = True

    make = String(required=True)
    model = String(required=True)
    year = Integer(required=True)
    owner_key = String(allow_none=True, missing=None)

    owner = relationship(Person, "owner_key")

    def __str__(self):
        return "<Car({} - {} - {})>".format(self.make, self.model, self.year)


persons = [
    Person(_key="kashif", name="Kashif Iftikhar", dob=datetime.today()),
    Person(_key="azeen", name="Azeen Kashif", dob=datetime.today()),
]
cars = [
    Car(make="Honda", model="Civic", year=1984, owner_key="kashif"),
    Car(make="Honda", model="Civic", year=1995, owner_key="kashif"),
    Car(make="Honda", model="Civic", year=1998, owner_key="Azeen"),
    Car(make="Honda", model="Civic", year=2001, owner_key="Azeen"),
    Car(make="Toyota", model="Corolla", year=1988, owner_key="kashif"),
    Car(make="Toyota", model="Corolla", year=2004, owner_key="Azeen"),
    Car(make="Mitsubishi", model="Lancer", year=2005, owner_key="Azeen"),
]


# Graph data
class Student(Collection):
    __collection__ = "students"

    _key = String(required=True)  # registration number
    name = String(required=True, allow_none=False)
    age = Integer(allow_none=True, missing=None)

    def __str__(self):
        return "<Student({})>".format(self.name)


class Teacher(Collection):
    __collection__ = "teachers"

    _key = String(required=True)  # employee id
    name = String(required=True)

    def __str__(self):
        return "<Teacher({})>".format(self.name)


class Subject(Collection):
    __collection__ = "subjects"

    _key = String(required=True)  # subject code
    name = String(required=True)
    credit_hours = Integer(allow_none=True, missing=None)
    has_labs = Boolean(missing=True)

    def __str__(self):
        return "<Subject({})>".format(self.name)


class SpecializesIn(Relation):
    __collection__ = "specializes_in"

    _key = String()
    expertise_level = String(
        required=True, options=["expert", "medium", "basic"]
    )

    def __str__(self):
        return "<SpecializesIn(_key={}, expertise_level={}, _from={}, _to={})>".format(
            self._key, self.expertise_level, self._from, self._to
        )


class Area(Collection):
    __collection__ = "areas"

    _key = String(required=True)  # area name


# DUMMY COLLECTIONS #


class DummyFromCol1(Collection):
    __collection__ = "dummy_from_col_1"
    _allow_extra_fields = True

    _key = String(required=True)


class DummyFromCol2(Collection):
    __collection__ = "dummy_from_col_2"

    _key = String(required=True)


class DummyRelation(Relation):
    __collection__ = "dummy_relation"

    _key = String(required=True)
    _from = String()
    _to = String()


class DummyToCol1(Collection):
    __collection__ = "dummy_to_col_1"

    _key = String(required=True)


class DummyToCol2(Collection):
    __collection__ = "dummy_to_col_2"

    _key = String(required=True)


class UniversityGraph(Graph):
    __graph__ = "university_graph"

    graph_connections = [
        # Using general Relation class for relationship
        GraphConnection(Student, Relation("studies"), Subject),
        GraphConnection(Teacher, Relation("teaches"), Subject),
        # Using specific classes for vertex and edges
        GraphConnection(Teacher, SpecializesIn, Subject),
        GraphConnection([Teacher, Student], Relation("resides_in"), Area),
    ]


students_data = [
    Student(_key="S1001", name="John Wayne", age=30),
    Student(_key="S1002", name="Lilly Parker", age=22),
    Student(_key="S1003", name="Cassandra Nix", age=25),
    Student(_key="S1004", name="Peter Parker", age=20),
]

teachers_data = [
    Teacher(_key="T001", name="Bruce Wayne"),
    Teacher(_key="T002", name="Barry Allen"),
    Teacher(_key="T003", name="Amanda Waller"),
]

subjects_data = [
    Subject(
        _key="ITP101",
        name="Introduction to Programming",
        credit_hours=4,
        has_labs=True,
    ),
    Subject(
        _key="CS102", name="Computer History", credit_hours=3, has_labs=False
    ),
    Subject(
        _key="CSOOP02",
        name="Object Oriented Programming",
        credit_hours=3,
        has_labs=True,
    ),
]

areas_data = [
    Area(_key="Gotham"),
    Area(_key="Metropolis"),
    Area(_key="StarCity"),
]

specializations_data = [
    SpecializesIn(
        _from="teachers/T001", _to="subjects/ITP101", expertise_level="medium"
    )
]


# FOR v, e, p IN 1..3 INBOUND 'areas/gotham'
# GRAPH 'university_graph'
# RETURN p

# Inheritance data
class Owner(Collection):
    __collection__ = "owner"

    _key = String()
    name = String()


class Vehicle(Collection):
    __collection__ = "vehicle"

    _inheritance_field = "discr"
    _inheritance_mapping = {
        'Bike': 'moto',
        'Truck': 'truck'
    }

    _key = String()
    brand = String()
    model = String()
    discr = String(required=True)


class Bike(Vehicle):
    motor_size = Float()


class Truck(Vehicle):
    traction_power = Float()


class Own(Relation):
    __collection__ = "own"


class OwnershipGraph(Graph):
    __graph__ = "ownership_graph"

    graph_connections = [
        GraphConnection(Owner, Own, Vehicle)
    ]


owner_data = [
    Owner(_key='001', name="John Doe"),
    Owner(_key='002', name="Billy the Kid"),
    Owner(_key='003', name="Lucky Luke")
]

vehicle_data = [
    Bike(_key='001', motor_size=125, brand='Harley Davidson', model='Hummer'),
    Truck(_key='002', traction_power=520, brand='Renault Trucks', model='T High')
]

own_data = [
    Own(_from='owner/001', _to='vehicle/001'),
    Own(_from='owner/002', _to='vehicle/002'),
    Own(_from='owner/003', _to='vehicle/001'),
    Own(_from='owner/003', _to='vehicle/002')
]


class Owner2(Collection):
    __collection__ = "owner"

    _key = String()
    name = String()


class Vehicle2(Collection):
    __collection__ = "vehicle"

    _key = String()
    brand = String()
    model = String()


class Bike2(Vehicle2):
    motor_size = Float()


class Truck2(Vehicle2):
    traction_power = Float()


class Own2(Relation):
    __collection__ = "own"


class OwnershipGraph2(Graph):
    __graph__ = "ownership_graph"

    graph_connections = [
        GraphConnection(Owner2, Own2, Vehicle2)
    ]

    def inheritance_mapping_resolver(self, col_name: str, doc_dict: dict = {}):
        if col_name == 'vehicle':
            if 'traction_power' in doc_dict:
                return Truck2
            else:
                return Bike2

        return self.vertices[col_name]


owner_data2 = [
    Owner2(_key='001', name="John Doe"),
    Owner2(_key='002', name="Billy the Kid"),
    Owner2(_key='003', name="Lucky Luke")
]

vehicle_data2 = [
    Bike2(_key='001', motor_size=125, brand='Harley Davidson', model='Hummer'),
    Truck2(_key='002', traction_power=520, brand='Renault Trucks', model='T High')
]

own_data2 = [
    Own2(_from='owner/001', _to='vehicle/001'),
    Own2(_from='owner/002', _to='vehicle/002'),
    Own2(_from='owner/003', _to='vehicle/001'),
    Own2(_from='owner/003', _to='vehicle/002')
]


# Multiple inheritance data

class People(Collection):
    __collection__ = "people"

    _key = String()
    name = String()


class Parent(People):
    work = String()


class Child(People):
    hobby = String()


class Boy(People):
    personality = String()


class Girl(People):
    hair_color = String()


class Father(Parent, Boy):
    wife_name = String()


class Mother(Parent, Girl):
    husband_name = String()


class Son(Child, Boy):
    sister_name = String()


class Daughter(Child, Girl):
    brother_name = String()


class PeopleGraph(Graph):
    __graph__ = "people_graph"

    graph_connections = [
        GraphConnection(People, Relation('resides_with'), People)
    ]

people_data = [
    Father(_key='001', name='Homer', work='Nuclear supervisor', personality='lazy', wife_name='Marge'),
    Mother(_key='002', name='Marge', work='None', hair_color='blue', husband_name='Homer'),
    Son(_key='003', name='Bart', hobby='Skateboard', personality='playful', sister_name='Lisa'),
    Daughter(_key='004', name='Lisa', hobby='Saxophone', hair_color='yellow', brother_name='Bart')
]

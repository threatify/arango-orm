"""
Sample data for testing.

Contains sample collections and graph for checking out arango-orm.
"""

import sys
from pprint import pprint as pp

from arango import ArangoClient  # pylint: disable=E0401
from arango_orm.fields import (  # pylint: disable=E0611
    String, Integer, Boolean)
from arango_orm.database import Database  # pylint: disable=E0401
from arango_orm.collections import Collection, Relation  # pylint: disable=E
from arango_orm.graph import Graph, GraphConnection  # pylint: disable=E0401


class Student(Collection):
    """Students collection."""

    __collection__ = 'students'

    _key = String(required=True)  # registration number
    name = String(required=True, allow_none=False)
    age = Integer()

    def __str__(self):
        """Friendlier string representation."""
        return "<Student({},{})>".format(self._key, self.name)


class Teacher(Collection):
    """Teachers collection."""

    __collection__ = 'teachers'

    _key = String(required=True)  # employee id
    name = String(required=True)

    def __str__(self):
        """Friendlier string representation."""
        return "<Teacher({})>".format(self.name)


class Subject(Collection):
    """Subjects collection."""

    __collection__ = 'subjects'

    _key = String(required=True)  # subject code
    name = String(required=True)
    credit_hours = Integer()
    has_labs = Boolean(missing=True)

    def __str__(self):
        """Friendlier string representation."""
        return "<Subject({})>".format(self.name)


class Area(Collection):
    """Areas collection."""

    __collection__ = 'areas'

    _key = String(required=True)  # area name


class SpecializesIn(Relation):
    """Teacher Specialization relation."""

    __collection__ = 'specializes_in'

    _key = String(required=True)
    expertise_level = String(
        required=True, options=["expert", "medium", "basic"])

    def __str__(self):
        """Friendlier string representation."""
        return "<SpecializesIn(_key=" + \
            "{}, expertise_level={}, _from={}, _to={})>".format(
                self._key, self.expertise_level, self._from, self._to)


class UniversityGraph(Graph):
    """University Graph."""

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
Usage: {} action [db] [username] [password] [protocol] [host] [port]

Supported actions are:

create_graph - Create the graph and all it's vertices and edges
drop_graph - Drop the graph and all it's vertices and edges
graph_test - Run some sample queries against the graph

Default values for optional args:
db: test_db
username: root
password:
protocol: http
host: 127.0.0.1
port: 8529
""".format(sys.argv[0])

    if len(sys.argv) < 2:
        print(usage)
        sys.exit(1)

    action = sys.argv[1]
    db_name = sys.argv[2] if len(sys.argv) > 2 else 'test_db'
    username = sys.argv[3] if len(sys.argv) > 3 else 'root'
    password = sys.argv[4] if len(sys.argv) > 4 else ''
    protocol = sys.argv[5] if len(sys.argv) > 5 else 'http'
    host = sys.argv[6] if len(sys.argv) > 6 else '127.0.0.1'
    port = int(sys.argv[7]) if len(sys.argv) > 7 else 8529

    client = ArangoClient(protocol=protocol, host=host, port=port)
    test_db = client.db(db_name, username=username, password=password)

    db = Database(test_db)

    uni_graph = UniversityGraph(connection=db)

    if action == 'create_graph':
        db.create_graph(uni_graph)
        data_create()
        print("Graph and data created!")

    elif action == 'drop_graph':
        db.drop_graph(uni_graph)
        print("Graph dropped")

    elif action == 'graph_test':
        bruce = db.query(Teacher).by_key("T001")
        uni_graph.expand(bruce, depth=1, direction='any')

        print('bruce._relations')
        pp(bruce._relations)

        students_of_bruce = [r._next for r in bruce._relations['teacher']]
        print('Students of Bruce')
        for s in students_of_bruce:
            pp(s)

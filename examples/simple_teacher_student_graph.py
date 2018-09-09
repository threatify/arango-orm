from arango import ArangoClient
from arango_orm import Database, Collection, Relation, Graph, GraphConnection
from arango_orm.fields import List, String, UUID, Integer, Boolean, DateTime


class Teacher(Collection):

    __collection__ = 'teachers'

    _key = String(required=True)  # employee id
    name = String(required=True)


class Student(Collection):

    __collection__ = 'students'

    _key = String(required=True)  # registration number
    name = String(required=True, allow_none=False)
    age = Integer()


class UniversityGraph(Graph):

    __graph__ = 'university_graph'

    graph_connections = [
        GraphConnection(Teacher, Relation("teaches"), Student)
    ]


client = ArangoClient()
test_db = client.db('test', username='test', password='test')
db = Database(test_db)
uni_graph = UniversityGraph(connection=db)

db.create_graph(uni_graph)  # This creates the graph and the collections

bruce = Teacher(_key='T001', name='Bruce')
barry = Student(_key='S001', name='Barry', age=30)
linda = Student(_key='S002', name='Linda', age=20)

db.add(bruce)
db.add(barry)
db.add(linda)

db.add(uni_graph.relation(bruce, Relation("teaches"), barry))
db.add(uni_graph.relation(bruce, Relation("teaches"), linda))


bruce = db.query(Teacher).by_key('T001')
uni_graph.expand(bruce, depth=1)
students_of_bruce = [r._next for r in bruce._relations['teaches']]

for s in students_of_bruce:
    print(s.name)

Python ORM Layer For ArangoDB
=============================

**arango_orm** is a python ORM layer inspired by SQLAlchemy but aimed to work with the multi-model database ArangoDB. It supports accessing both collections and graphs using the ORM. The actual communication with the database is done using **python-arango** (the database driver for accessing arangodb from python) and object serialization and deserialization is handled using **marshmallow**


Connecting to a Database
-------------------------

::

    from arango import ArangoClient
    from arango_orm import Database
    
    client = ArangoClient(username='test', password='test')
    test_db = client.db('test')
    
    db = Database(test_db)

Working With Collections
-------------------------

First we need to define data models (similar to SQLAlchemy's models) to specify what data our collection(s) will contain and how to marshall it::


    from arango_orm import Collection
    from marshmallow import Schema
    from marshmallow.fields import String, Date
    
    class Student(Collection):
    
        __collection__ = 'students'
    
        class _Schema(Schema):
            _key = String(required=True)  # registration number
            name = String(required=True, allow_none=False)
            dob = Date()


Create Collection in the Database
_________________________________

::

    db.create_collection(Student)


Drop a Collection
__________________

::

    db.drop_collection(Student)


Add Records
___________

::

    from datetime import date
    s = Student(name='test', _key='12312', dob=date(year=2016, month=9, day=12))
    db.add(s)
    print(s._id)  # students/12312


Get Total Records in the Collection
___________________________________

::

    db.query(Student).count()


Get Record By Key
_________________

::

    s = db.query(Student).by_key('12312')


Update a Record
________________

::

    s = db.query(Student).by_key('12312')
    s.name = 'Anonymous'
    db.update(s)

Delete a Record
________________

::

    s = db.query(Student).by_key('12312')
    db.delete(s)

Get All Records in a Collection
________________________________

::

    students = db.query(Student).all()


Filter Records
______________

Using bind parameters (recommended)::

    records = db.query(Student).filter("name==@name", name='Anonymous').all()

Using plain condition strings (not safe in case of unsanitized user supplied input)::

    records = db.query(Student).filter("name=='Anonymous'").all()


Filter Using OR
_______________

::

    # Get all documents where student name starts with A or B
    records = db.query(Student).filter(
                "LIKE(rec.name, 'A%')", prepend_rec_name=False).filter(
                "LIKE(rec.name, 'B%')", prepend_rec_name=False, _or=True).all()


Filter, Sort and Limit
______________________

::

    # Last 5 students with names starting with A
    records = db.query(Student).filter(
                "LIKE(rec.name, 'A%')", prepend_rec_name=False).sort("name DESC").limit(5).all()


Update Multiple Records
_______________________

::

    db.query(Student).filter("name==@name", name='Anonymous').update(name='Mr. Anonymous')


Delete Multiple Records
_______________________

::

    db.query(Student).filter("LIKE(rec.name, 'test%')", prepend_rec_name=False).delete()


Delete All Records
___________________

::

    db.query(Student).delete()


Query Using AQL
________________

::

    db.add(Student(name='test1', _key='12345', dob=date(year=2016, month=9, day=12)))
    db.add(Student(name='test2', _key='22346', dob=date(year=2015, month=9, day=12)))
    
    students = [Student._load(s) for s in db.aql.execute("FOR st IN students RETURN st")]


Working With Graphs
-------------------

Working with graphs involves creating collection classes and optionally Edge/Relation classes. Users can use the built-in Relation class for specifying relations but if relations need to contain extra attributes then it's required to create a sub-class of Relation class. Graph functionality is explain below with the help of a university graph example containing students, teachers, subjects and the areas where students and teachers reside in.

First we create some collections and relationships::

    from marshmallow import Schema
    from marshmallow.fields import String, Date, Integer, Boolean
    from arango_orm import Collection, Relation, Graph, GraphConnection


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
    

    class Area(Collection):
    
        __collection__ = 'areas'
    
        class _Schema(Schema):
            _key = String(required=True)  # area name

    
    class SpecializesIn(Relation):
    
        __collection__ = 'specializes_in'
    
        class _Schema(Schema):
            expertise_level = String(required=True, options=["expert", "medium", "basic"])
    
        def __str__(self):
            return "<SpecializesIn(_key={}, expertise_level={}, _from={}, _to={})>".format(
                self._key, self.expertise_level, self._from, self._to)


Next we sub-class the Graph class to specify the relationships between the various collections

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

Now it's time to create the graph. Note that we don't need to create the collections individually, creating the graph will create all collections that it contains::

    from arango import ArangoClient
    from arango_orm.database import Database
    
    client = ArangoClient(username='test', password='test')
    test_db = client.db('test')
    
    db = Database(test_db)
    
    uni_graph = UniversityGraph(connection=db)
    db.create_graph(uni_graph)


Now the graph and all it's collections have been created, we can verify their existence::

    [c['name'] for c in db.collections()]
    db.graphs()

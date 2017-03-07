Python ORM Layer For ArangoDB
=============================

**arango_orm** is a python ORM layer inspired by SQLAlchemy but aimed to work with the multi-model database ArangoDB. It supports accessing both collections and graphs using the ORM. The actual communication with the database is done using **python-arango** (the database driver for accessing arangodb from python) and object serialization and deserialization is handled using **marshmallow**

Installation:
-------------

::

    pip install arango-orm


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
        _index = [{'type': 'hash', fields: ['name'], unique=False}]
    
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


Next we sub-class the Graph class to specify the relationships between the various collections::

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

Now let's insert some data into our graph::

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
    
    for s in students_data:
        db.add(s)
    
    for t in teachers_data:
        db.add(t)
    
    for s in subjects_data:
        db.add(s)
    
    for a in areas_data:
        db.add(a)

Next let's add some relations, we can add relations by manually adding the relation/edge record into the edge collection, like::

    db.add(SpecializesIn(_from="teachers/T001", _to="subjects/ITP101", expertise_level="medium"))

Or we can use the graph object's relation method to generate a relation document from given objects::

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

With our graph populated with some sample data, let's explore the ways we can work with the graph.


Expanding Documents
___________________

We can expand any Collection (not Relation) object to access the data that is linked to it. We can sepcify which links ('inbound', 'outbound', 'any') to expand and the depth to which those should be expanded to. Let's see all immediate connections that Bruce Wayne has in our graph::

    bruce = db.query(Teacher).by_key("T001")
    uni_graph.expand(bruce, depth=1, direction='any')

Graph expansion on an object adds a **_relations** dictionary that contains all the relations for the object according to the expansion criteria::

    bruce._relations

Returns::

    {
    'resides_in': [<Relation(_key=4205290, _from=teachers/T001, _to=areas/Gotham)>],
    'specializes_in': [<SpecializesIn(_key=4205114, expertise_level=medium, _from=teachers/T001, _to=subjects/ITP101)>,
     <SpecializesIn(_key=4205271, expertise_level=expert, _from=teachers/T001, _to=subjects/CS102)>,
     <SpecializesIn(_key=4205268, expertise_level=medium, _from=teachers/T001, _to=subjects/CSOOP02)>],
    'teaches': [<Relation(_key=4205280, _from=teachers/T001, _to=subjects/CSOOP02)>]
    }

We can use _from and _to of a relation object to access the id's for both sides of the link. We also have _object_from and _object_to to access the objects on both sides, for example::

    bruce._relations['resides_in'][0]._object_from.name
    # 'Bruce Wayne'
    
    bruce._relations['resides_in'][0]._object_to._key
    # 'Gotham'

There is also a special attribute called **_next** that allows accessing the other side of the relationship irrespective of the relationship direction. For example, for outbound relationships the _object_from contains the source object while for inbound_relationships _object_to contains the source object. But if we're only interested in traversal of the graph then it's more useful at times to access the other side of the relationship w.r.t the current object irrespective of it's direction::

    bruce._relations['resides_in'][0]._next._key
    # 'Gotham'

Let's expand the bruce object to 2 levels and see **_next** in more action::

    uni_graph.expand(bruce, depth=2)
    
    # All relations of the area where bruce resides in
    bruce._relations['resides_in'][0]._object_to._relations
    # -> {'resides_in': [<Relation(_key=4205300, _from=students/S1001, _to=areas/Gotham)>]}
    
    # Name of the student that resides in the same area as bruce
    bruce._relations['resides_in'][0]._object_to._relations['resides_in'][0]._object_from.name
    # 'John Wayne'
    
    # The same action using _next without worrying about direction
    bruce._relations['resides_in'][0]._next._relations['resides_in'][0]._next.name
    # 'John Wayne'
    
    # Get names of all people that reside in the same area and Bruce Wayne
    [p._next.name for p in bruce._relations['resides_in'][0]._next._relations['resides_in']]
    # ['John Wayne']


Graph Traversal Using AQL
__________________________

The graph module also supports traversals using AQL, the results are converted to objects and have the
same structure as graph.expand method::

    obj = uni_graph.aql("FOR v, e, p IN 1..2 INBOUND 'areas/Gotham' GRAPH 'university_graph' RETURN p")
    print(obj._key)
    # Gotham
    
    gotham_residents = [rel._next.name for rel in obj._relations['resides_in']]
    print(gotham_residents)
    # ['Bruce Wayne', 'John Wayne']

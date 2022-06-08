Python ORM Layer For ArangoDB
=============================

**arango_orm** is a python ORM layer inspired by SQLAlchemy but aimed to work
with the multi-model database ArangoDB. It supports accessing both collections
and graphs using the ORM. The actual communication with the database is done
using **python-arango** (the database driver for accessing arangodb from
python) and object serialization and de-serialization is handled using
**marshmallow**.


Installation:
-------------

::

    pip install arango-orm


Connecting to a Database
-------------------------

.. code-block:: python

    from arango import ArangoClient
    from arango_orm import Database

    client = ArangoClient(hosts='http://localhost:8529')
    test_db = client.db('test', username='test', password='test')

    db = Database(test_db)


Using a Connection Pool
-----------------------

Note: This is deprecated since python arango version 5.0. Since now the base
library supports the hosts parameter. This will be removed in future versions.
Users should instead use the pool in ArangoClient like:

.. code-block:: python

  client = ArangoClient(
    hosts=['http://host1:8529', 'http://host2:8529'],
    host_resolver='roundrobin'
  )


Connection pools allow using multiple connections for accessing the database.
Though these can be used on a single machine setup, they are more useful to use
with arango clusters.

Connection pools support the same methods and properties that the Database class
does. So they can be used interchangeably with Database.

.. code-block:: python

    from arango import ArangoClient
    from arango_orm import ConnectionPool

    client1 = ArangoClient(protocol='http', host='localhost', port=8529)
    client2 = ArangoClient(protocol='http', host='127.0.0.1', port=8529)

    db = ConnectionPool([client1, client2], 'test', 'test', 'test')


Working With Collections
-------------------------

First we need to define data models (similar to SQLAlchemy's models) to specify what data our collection(s) will contain and how to marshal it

.. code-block:: python

    from arango_orm import Collection
    from arango_orm.fields import String, Date

    class Student(Collection):

        __collection__ = 'students'
        _index = [{'type': 'hash', fields: ['name'], unique=False}]

        _key = String(required=True)  # registration number
        name = String(required=True, allow_none=False)
        dob = Date()


Create Collection in the Database
_________________________________

.. code-block:: python

    db.create_collection(Student)


Drop a Collection
__________________

.. code-block:: python

    db.drop_collection(Student)

Check if a collection exists
____________________________

.. code-block:: python

    db.has_collection(Student)
    db.has_collection('students')

Add Records
___________

.. code-block:: python

    from datetime import date
    s = Student(name='test', _key='12312', dob=date(year=2016, month=9, day=12))
    db.add(s)
    print(s._id)  # students/12312


Get Total Records in the Collection
___________________________________

.. code-block:: python

    db.query(Student).count()


Get Record By Key
_________________

.. code-block:: python

    s = db.query(Student).by_key('12312')


Update a Record
________________

.. code-block:: python

    s = db.query(Student).by_key('12312')
    s.name = 'Anonymous'
    db.update(s)

Delete a Record
________________

.. code-block:: python

    s = db.query(Student).by_key('12312')
    db.delete(s)

Get All Records in a Collection
________________________________

.. code-block:: python

    students = db.query(Student).all()

Get First Record Matching the Query
____________________________________

.. code-block:: python

    first_student = db.query(Student).first()

Filter Records
______________

Using bind parameters (recommended)

.. code-block:: python

    records = db.query(Student).filter("name==@name", name='Anonymous').all()

Using plain condition strings (not safe in case of unsanitized user supplied input)

.. code-block:: python

    records = db.query(Student).filter("name=='Anonymous'").all()


Filter Using OR
_______________

.. code-block:: python

    # Get all documents where student name starts with A or B
    records = db.query(Student).filter(
                "LIKE(rec.name, 'A%')", prepend_rec_name=False).filter(
                "LIKE(rec.name, 'B%')", prepend_rec_name=False, _or=True).all()


Filter, Sort and Limit
______________________

.. code-block:: python

    # Last 5 students with names starting with A
    records = db.query(Student).filter(
                "LIKE(rec.name, 'A%')", prepend_rec_name=False).sort("name DESC").limit(5).all()

    # Query students with pagination (limit&offset)
    page_num, per_page = 2, 10
    page = db.query(Student).sort("name DESC").limit(per_page, start_from=(page_num - 1) * per_page)

Fetch Only Some Fields
______________________

    .. code-block:: python

        c = db.query(Student).limit(2).returns('_key', 'name').first()

Update Multiple Records
_______________________

.. code-block:: python

    db.query(Student).filter("name==@name", name='Anonymous').update(name='Mr. Anonymous')


Delete Multiple Records
_______________________

.. code-block:: python

    db.query(Student).filter("LIKE(rec.name, 'test%')", prepend_rec_name=False).delete()


Delete All Records
___________________

.. code-block:: python

    db.query(Student).delete()



Bulk Create Records
_______________________

.. code-block:: python

    s1 = Student(name='test1', _key='12345', dob=date(year=2016, month=9, day=12))
    s2 = Student(name='test2', _key='22346', dob=date(year=2015, month=9, day=12)
    car1 = Car(make="Honda", model="Fiat", year=2010)
    car2 = Car(make="Honda", model="Skoda", year=2015)

    db.bulk_add(entity_list=[p_ref_10, p_ref_11, car1, car2])


Bulk Update Records
_______________________

.. code-block:: python

    p_ref1 = db.query(Person).by_key("12312")
    p_ref2 = db.query(Person).by_key("12345")
    p_ref1.name = "Bruce"
    p_ref2.name = "Eliza"
    db.bulk_update(entity_list=[p_ref1, p_ref2])


Query Using AQL
________________

.. code-block:: python

    db.add(Student(name='test1', _key='12345', dob=date(year=2016, month=9, day=12)))
    db.add(Student(name='test2', _key='22346', dob=date(year=2015, month=9, day=12)))

    students = [Student._load(s) for s in db.aql.execute("FOR st IN students RETURN st")]

Reference Fields
----------------

Reference fields allow linking documents from another collection class within a collection instance.
These are similar in functionality to SQLAlchemy's relationship function.

.. code-block:: python

    from arango import ArangoClient
    from arango_orm.database import Database

    from arango_orm.fields import String
    from arango_orm import Collection, Relation, Graph, GraphConnection
    from arango_orm.references import relationship, graph_relationship


    class Person(Collection):

        __collection__ = 'persons'

        _index = [{'type': 'hash', 'unique': False, 'fields': ['name']}]
        _allow_extra_fields = False  # prevent extra properties from saving into DB

        _key = String(required=True)
        name = String(required=True, allow_none=False)

        cars = relationship(__name__ + ".Car", '_key', target_field='owner_key')

        def __str__(self):
            return "<Person(" + self.name + ")>"


    class Car(Collection):

        __collection__ = 'cars'
        _allow_extra_fields = True

        make = String(required=True)
        model = String(required=True)
        year = Integer(required=True)
        owner_key = String()

        owner = relationship(Person, 'owner_key', cache=False)

        def __str__(self):
            return "<Car({} - {} - {})>".format(self.make, self.model, self.year)

    client = ArangoClient(hosts='http://localhost:8529')
    test_db = client.db('test', username='test', password='test')
    db = Database(test_db)

    p = Person(_key='kashif', name='Kashif Iftikhar')
    db.add(p)
    p2 = Person(_key='azeen', name='Azeen Kashif')
    db.add(p2)

    c1 = Car(make='Honda', model='Civic', year=1984, owner_key='kashif')
    db.add(c1)

    c2 = Car(make='Mitsubishi', model='Lancer', year=2005, owner_key='kashif')
    db.add(c2)

    c3 = Car(make='Acme', model='Toy Racer', year=2016, owner_key='azeen')
    db.add(c3)

    print(c1.owner)
    print(c1.owner.name)
    print(c2.owner.name)
    print(c3.owner.name)

    print(p.cars)
    print(p.cars[0].make)
    print(p2.cars)


Working With Graphs
-------------------

Working with graphs involves creating collection classes and optionally Edge/Relation classes. Users can use the built-in Relation class for specifying relations but if relations need to contain extra attributes then it's required to create a sub-class of Relation class. Graph functionality is explain below with the help of a university graph example containing students, teachers, subjects and the areas where students and teachers reside in.

First we create some collections and relationships

.. code-block:: python

    from arango_orm.fields import String, Date, Integer, Boolean
    from arango_orm import Collection, Relation, Graph, GraphConnection


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


    class Area(Collection):

        __collection__ = 'areas'

        _key = String(required=True)  # area name


    class SpecializesIn(Relation):

        __collection__ = 'specializes_in'

        expertise_level = String(required=True, options=["expert", "medium", "basic"])

        def __str__(self):
            return "<SpecializesIn(_key={}, expertise_level={}, _from={}, _to={})>".format(
                self._key, self.expertise_level, self._from, self._to)


Next we sub-class the Graph class to specify the relationships between the various collections

.. code-block:: python

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

Now it's time to create the graph. Note that we don't need to create the collections individually, creating the graph will create all collections that it contains

.. code-block:: python

    from arango import ArangoClient
    from arango_orm.database import Database

    client = ArangoClient(hosts='http://localhost:8529')
    test_db = client.db('test', username='test', password='test')

    db = Database(test_db)

    uni_graph = UniversityGraph(connection=db)
    db.create_graph(uni_graph)


Now the graph and all its collections have been created, we can verify their existence:

.. code-block:: python

    [c['name'] for c in db.collections()]
    db.graphs()

Now let's insert some data into our graph:

.. code-block:: python

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

Next let's add some relations, we can add relations by manually adding the relation/edge record into the edge collection, like:

.. code-block:: python

    db.add(SpecializesIn(_from="teachers/T001", _to="subjects/ITP101", expertise_level="medium"))

Or we can use the graph object's relation method to generate a relation document from given objects:

.. code-block:: python

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

We can expand any Collection (not Relation) object to access the data that is linked to it. We can sepcify which links ('inbound', 'outbound', 'any') to expand and the depth to which those should be expanded to. Let's see all immediate connections that Bruce Wayne has in our graph:

.. code-block:: python

    bruce = db.query(Teacher).by_key("T001")
    uni_graph.expand(bruce, depth=1, direction='any')

Graph expansion on an object adds a **_relations** dictionary that contains all the relations for the object according to the expansion criteria:

.. code-block:: python

    bruce._relations

Returns::

    {
    'resides_in': [<Relation(_key=4205290, _from=teachers/T001, _to=areas/Gotham)>],
    'specializes_in': [<SpecializesIn(_key=4205114, expertise_level=medium, _from=teachers/T001, _to=subjects/ITP101)>,
     <SpecializesIn(_key=4205271, expertise_level=expert, _from=teachers/T001, _to=subjects/CS102)>,
     <SpecializesIn(_key=4205268, expertise_level=medium, _from=teachers/T001, _to=subjects/CSOOP02)>],
    'teaches': [<Relation(_key=4205280, _from=teachers/T001, _to=subjects/CSOOP02)>]
    }

We can use _from and _to of a relation object to access the id's for both sides of the link. We also have _object_from and _object_to to access the objects on both sides, for example:

.. code-block:: python

    bruce._relations['resides_in'][0]._object_from.name
    # 'Bruce Wayne'

    bruce._relations['resides_in'][0]._object_to._key
    # 'Gotham'

There is also a special attribute called **_next** that allows accessing the other side of the relationship irrespective of the relationship direction. For example, for outbound relationships the _object_from contains the source object while for inbound_relationships _object_to contains the source object. But if we're only interested in traversal of the graph then it's more useful at times to access the other side of the relationship w.r.t the current object irrespective of it's direction:

.. code-block:: python

    bruce._relations['resides_in'][0]._next._key
    # 'Gotham'

Let's expand the bruce object to 2 levels and see **_next** in more action:

.. code-block:: python

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


Inheritance Mapping
__________________________

For inheritance mapping, **arango_orm** offers you two ways to define it.

1. Discriminator field/mapping:

Discriminator field/mapping are defined at entity level:

.. code-block:: python

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
        # discr field match what you defined in _inheritance_field
        # the field type depends on the values of your _inheritance_mapping
        discr = String(required=True)


    class Bike(Vehicle):
        motor_size = Float()


    class Truck(Vehicle):
        traction_power = Float()


2. Inheritance mapping resolver:

The `inheritance_mapping_resolver` is a function defined at graph level; it allows you to make either a simple test
on a discriminator field, or complex inference

.. code-block:: python

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


Graph Traversal Using AQL
__________________________

The graph module also supports traversals using AQL, the results are converted to objects and have the
same structure as graph.expand method:

.. code-block:: python

    obj = uni_graph.aql("FOR v, e, p IN 1..2 INBOUND 'areas/Gotham' GRAPH 'university_graph' RETURN p")
    print(obj._key)
    # Gotham

    gotham_residents = [rel._next.name for rel in obj._relations['resides_in']]
    print(gotham_residents)
    # ['Bruce Wayne', 'John Wayne']


For Developers
==============

Running the Test Cases
----------------------

```bash
ARANGO_HOSTS="http://127.0.0.1:8529" ARANGO_USERNAME=root ARANGO_PASSWORD=toor ARANGO_DATABASE=test_db pytest tests
```

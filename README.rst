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

::

    records = db.query(Student).filter("name==@name", name='Anonymous').all()


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


Query Using AQL
________________

::

    db.add(Student(name='test1', _key='12345', dob=date(year=2016, month=9, day=12)))
    db.add(Student(name='test2', _key='22346', dob=date(year=2015, month=9, day=12)))
    
    students = [Student._load(s) for s in db.aql.execute("FOR st IN students RETURN st")]

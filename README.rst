Python ORM Layer For ArangoDB
=============================

**arango_orm** is a python ORM layer inspired by SQLAlchemy but aimed to work with the multi-model database ArangoDB. It supports accessing both collections and graphs using the ORM. The actual communication with the database is done using **python-arango** (the database driver for accessing arangodb from python) and object serialization and deserialization is handled using **marshmallow**


Connecting to a Database
-------------------------

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

    db.create_collection(Student)


Add Records
___________

    s = Student(name='test', _key='12312', dob=date(year=2016, month=9, day=12))
    db.add(s)


Get Total Records in the Collection
___________________________________

    db.query(Person).count()


Get Record By Key
_________________

    s = db.query(Student).by_key('12312')


Update a Record
________________

    s = db.query(Student).by_key('12312')
    s.name = 'Anonymous'
    db.update(s)

Delete a Record
________________

    s = db.query(Student).by_key('12312')
    db.delete(s)

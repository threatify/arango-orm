CHANGES
=======

Version 0.6.1
-------------

- Support for specifiying a normal name for the `_key` field (only for models, for querying etc still need to use `_key`)

  .. code-block:: python

    class Person(Collection):

      __collection__ = "persons"

      _key_field = 'name'

      name = String(required=True, allow_none=False)
      age = Integer(allow_none=True, missing=None)

    p1 = Person(_key='abc', age=30)
    print(p1._key)
    print(p1.name)  # same as p1._key
    print(p1.age)

    p2 = Person()
    p2.name = 'xyz'
    print(p2._key)
    print(p2.name)  # same as p2._key
    
Version 0.6
-----------

- Code updated to work with latest marshmallow (3.7.0).

- Validation is done on record add and update time too. Fixes #70. Previously
  data was added without validation and when it was read back, validation was done
  at that time (default marshmallow behavior) and caused validation errors.

- [Backward incompatible] Setting _key field to require=True means that it's value
  should always be provided and is not to be auto-generated. To keep the previous
  behavior do not set `required=True` for the field. This will allow both setting
  it or having it auto generated.

  .. code-block:: python

    # allows _key auto-generation
    class Person(Collection):

        __collection__ = "persons"

        _key = String()
        name = String(required=True, allow_none=False)
        age = Integer(allow_none=True, missing=None)
        dob = Date(allow_none=True, missing=None)

    # This will not allow _key auto-generation
    class Person(Collection):

        __collection__ = "persons"

        _key = String(required=True)
        name = String(required=True, allow_none=False)
        age = Integer(allow_none=True, missing=None)
        dob = Date(allow_none=True, missing=None)


Version 0.5.9
-------------

- Support for specifying cursor ttl for queries. Otherwise arangodb has a small delay in returning records after record number 1000 which causes no cursor errors. Thanks @wonderbeyond for the PR.

Version 0.5.8
-------------

- Bug fix for https://github.com/threatify/arango-orm/issues/55

Version 0.5.7
--------------

- Support for Database.drop_all

Version 0.5.6
--------------

- Bugfix: Handling pre_update properly

Version 0.5.5
--------------

- Graph.expand has new parameter 'only' that allows traversing only records
  that belong to the collections specified in the only list.
  :param only: If given should be a string, Collection class or list of
      strings or collection classes containing target collection names of
      documents (vertices) that should be fetched.
      Any vertices found in traversal that don't belong to the specified
      collection names given in this parameter will be ignored.


Version 0.5.4
-------------

- Database.add supports if_present parameter so if a record already exists
  then instead of returning error it can be updated or the record exists error
  is ignored.

Version 0.5.3
-------------

- bugfix #51 - _only parameter for relations
- Updated examples/university_graph for easier creation and deletion of sample
  graph with data and allowing server protocol, host, port, database, username
  and password specification on the command line.

Version 0.5.2
-------------

- _only parameter for collections

Version 0.5.1
-------------

- Query.by_key raises DocumentNotFoundError if document does not exist

Version 0.5
-----------

- Connection pool support.
- Support fetching only partial fields while querying collections
- Collections now raise SerializationError instead of RuntimeError when loading or dumping data to the db fails.

Version 0.4
-----------

- Database.has_collection method.
- Examples and README updated to use ArangoClient correctly for the 4.x version.
- Fixed #10 - Collections now raise SerializationError instead of RuntimeError
  when loading or dumping data to the db fails.

Version 0.3.1
-------------

- Query.first() and Query.one() methods implementation to return the first record that matches the query

Version 0.3
-----------

- Schema fields are now be defined inside the main model class instead of a nested _Schema child class
- Allow extra fields not present in the schema to be present in collections without any validation or type conversion
- Load and dump extra fields only if _allow_extra_fields is set to True for the collection class
- Bound db to model object. If an object has interacted with the db then it's _db attribute points to the database
- Collections now have _pre_process and _post_process methods that get called before and after data loading into the collection respectively
- Database.create_all method creates all collections, relations, graphs (with their edge definitions) that are passed onto it as a list.
- Database.update_graph creates collections, relations, edge definitions and drops or replaces edge definitions if they have changed. Does not drop any collection or relation.


Version 0.2
-----------

- Support for creating indices by defining _index attribute in model definition

Version 0.2.1
-------------

- Graph creation also supports creating indices from collection class _index attribute
- Support for passing collection create options as supported by `python-arango database.create_collection <http://python-driver-for-arangodb.readthedocs.io/en/stable/classes.html#arango.database.Database.create_collection>`_ method to database.create_colltion method

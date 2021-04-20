.. arango-orm documentation master file, created by
   sphinx-quickstart on Thu Jul 23 14:35:07 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Python ORM Layer For ArangoDB
=============================

**arango_orm** is a python ORM layer inspired by SQLAlchemy but aimed to work
with the multi-model database ArangoDB. It supports accessing both collections
and graphs using the ORM. The actual communication with the database is done
using **python-arango** (the database driver for accessing arangodb from
python) and object serialization and de-serialization is handled using
**marshmallow**.

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   getting-started
   api-reference



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

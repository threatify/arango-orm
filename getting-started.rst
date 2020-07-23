Getting started contributing to Arango ORM
==========================================
Docker
------
To initially get started with docker, ensure you have docker(https://www.docker.com/) installed.

Once successfully installed and setup, run

.. code-block:: shell-session
docker-compose --build

This will build the development enviroment, spinning up
 - an Arango instance (arango)
 - a test image (arango_orm)

To run tests from there, run

.. code-block:: shell-session
docker-compose run arango_orm pytest tests/

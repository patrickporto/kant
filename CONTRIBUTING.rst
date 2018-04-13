Contributing
============

Kant is open-source and very open to contributions

Submitting patches (bugfix, features, ...)
------------------------------------------

If you want to contribute some code:

1. fork the `official kant repository`.
2. create a branch with an explicit name (like ``new-feature`` or ``issue-XXX``)
3. do your work in it
4. add you change to the changelog
5. submit your pull-request

There are some rules to follow:

- your contribution should be documented (if needed)
- your contribution should be tested and the test suite should pass successfully
- your code should be mostly Code Style compatible.

You need to install some dependencies to develop on kant:

.. code-block:: console

    $ pipenv --three install --dev

You can preview the documentation:

.. code-block:: console

    $ sphinx-autobuild docs _build/html

.. _official kant repository: https://github.com/patrickporto/kant
.. _official bugtracker: https://github.com/patrickporto/kant/issues

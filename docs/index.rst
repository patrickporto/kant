Kant: Event Sourcing and CQRS
================================

.. image:: https://badges.frapsoft.com/os/mit/mit.png?v=103
    :target: https://opensource.org/licenses/mit-license.php

.. image:: https://travis-ci.org/patrickporto/kant.svg?branch=master
    :target: https://travis-ci.org/patrickporto/kant

.. image:: https://codecov.io/github/patrickporto/kant/coverage.svg?branch=master
    :target: https://codecov.io/github/patrickporto/kant?branch=master

.. image:: https://img.shields.io/pypi/v/kant.svg
    :target: https://pypi.python.org/pypi/kant

.. image:: https://img.shields.io/pypi/pyversions/kant.svg
    :target: https://pypi.python.org/pypi/kant

.. image:: https://img.shields.io/pypi/implementation/kant.svg
    :target: https://pypi.python.org/pypi/kant

**Kant** is a framework for Event Sourcing and CQRS for Python with a focus on simplicity a performance.

Here’s what it looks like:

.. code-block:: python3

    from kant.eventstore import connect

    await connect(user='user', password='user', database='database')

    # create event store for bank_account
    conn.create_keyspace('bank_account')

    # create events
    bank_account_created = BankAccountCreated(
        id=123,
        owner='John Doe',
    )
    deposit_performed = DepositPerformed(
        amount=20,
    )

    bank_account = BankAccount()
    bank_account.dispatch([bank_account_created, deposit_performed])
    bank_account.save()

    stored_bank_account = BankAccount.objects.get(123)


**Kant** is licensed_ under the MIT and it officially supports Python 3.5 or later.

Get It Now
----------

.. code-block:: console

    $ pip install kant


User Guide
----------

This part of the documentation is focused primarily on teaching you how to use Kant.

.. toctree::
   :maxdepth: 2

   installation
   events
   commands
   projections
   eventstore
   testing

API Reference
-------------

This part of the documentation is focused on detailing the various bits and pieces of the Kant developer interface.

.. toctree::
   :maxdepth: 2

   reference

.. _licensed: https://opensource.org/licenses/mit-license.php

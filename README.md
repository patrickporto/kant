# Kant Framework
[![Build Status](https://travis-ci.org/patrickporto/kant.svg?branch=master)](https://travis-ci.org/patrickporto/kant)
[![codecov.io](https://codecov.io/github/patrickporto/kant/coverage.svg?branch=master)](https://codecov.io/github/patrickporto/kant?branch=master)
[![PyPI Package latest release](https://img.shields.io/pypi/v/kant.svg)](https://pypi.python.org/pypi/kant)
[![Supported versions](https://img.shields.io/pypi/pyversions/kant.svg)](https://pypi.python.org/pypi/kant)
[![Supported implementations](https://img.shields.io/pypi/implementation/kant.svg)](https://pypi.python.org/pypi/kant)


A CQRS and Event Sourcing framework, safe for humans.

## Feature Support

* Event Store
* Pessimistic and Optimistic concurrency control
* JSON serialization
* Snapshots **[IN PROGRESS]**
* Projections **[IN PROGRESS]**

Kant officially supports Python 3.5-3.6.

## Getting started

Create declarative events

```python
from kant.events import models

class BankAccountCreated(models.EventModel):
    id = models.CUIDField(primary_key=True)
    owner = models.CharField()

class DepositPerformed(models.EventModel):
    amount = models.DecimalField()
```

Create aggregate to apply events

```python
from kant.aggregates import models

class BankAccount(models.Aggregate):
    id = models.CUIDField()
    owner = models.CharField()
    balance = models.DecimalField()

    def apply_bank_account_created(self, event):
        self.id = event.id
        self.owner = event.owner
        self.balance = 0

    def apply_deposit_performed(self, event):
        self.balance += event.amount
```

Now, save the events

```python
from kant.eventstore.connection import connect

conn = await connect(user='user', password='user', database='database')

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

# insert the events into EventStore
async with conn.open('bank_account/{}'.format(bank_account.id), 'w') as eventstream:
    eventstream += bank_account.get_events()
```

Load the events from EventStore
```python
async with conn.open('bank_account/123', 'w') as eventstream:
    bank_account = BankAccount.from_stream(eventstream)
```

## Installing
To install Kant, simply use [pipenv](pipenv.org) (or pip)

```bash
$ pipenv install kant
```



## Contributing

Please, read the contribute guide [CONTRIBUTING](CONTRIBUTING.md).

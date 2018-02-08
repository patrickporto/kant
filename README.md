# Kant Framework
[![Build Status](https://travis-ci.org/patrickporto/kant.svg?branch=master)](https://travis-ci.org/patrickporto/kant)
[![codecov.io](https://codecov.io/github/patrickporto/kant/coverage.svg?branch=master)](https://codecov.io/github/patrickporto/kant?branch=master)
[![PyPI Package latest release](https://img.shields.io/pypi/v/kant.svg)](https://pypi.python.org/pypi/kant)
[![Supported versions](https://img.shields.io/pypi/pyversions/kant.svg)](https://pypi.python.org/pypi/kant)
[![Supported implementations](https://img.shields.io/pypi/implementation/kant.svg)](https://pypi.python.org/pypi/kant)


A CQRS and Event Sourcing framework, safe for humans.

## Feature Support

* Event Store
* Optimistic concurrency control
* JSON serialization
* SQLAlchemy Projections
* Snapshots **[IN PROGRESS]**

Kant officially supports Python 3.5-3.6.

## Getting started

Create declarative events

```python
from kant import events

class BankAccountCreated(events.Event):
    id = events.CUIDField(primary_key=True)
    owner = events.CharField()

class DepositPerformed(events.Event):
    amount = events.DecimalField()
```

Create aggregate to apply events

```python
from kant import aggregates

class BankAccount(aggregates.Aggregate):
    id = aggregates.CUIDField()
    owner = aggregates.CharField()
    balance = aggregates.DecimalField()

    def apply_bank_account_created(self, event):
        self.id = event.id
        self.owner = event.owner
        self.balance = 0

    def apply_deposit_performed(self, event):
        self.balance += event.amount
```

Now, save the events

```python
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
```

## Installing
To install Kant, simply use [pipenv](pipenv.org) (or pip)

```bash
$ pipenv install kant
```



## Contributing

Please, read the contribute guide [CONTRIBUTING](CONTRIBUTING.md).

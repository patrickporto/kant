# Kant Framework
[![Build Status](https://travis-ci.org/patrickporto/kant.svg?branch=master)](https://travis-ci.org/patrickporto/kant)
[![codecov.io](https://codecov.io/github/patrickporto/kant/coverage.svg?branch=master)](https://codecov.io/github/patrickporto/kant?branch=master)
[![PyPI Package latest release](https://img.shields.io/pypi/v/kant.svg)](https://pypi.python.org/pypi/kant)
[![Supported versions](https://img.shields.io/pypi/pyversions/kant.svg)](https://pypi.python.org/pypi/kant)
[![Supported implementations](https://img.shields.io/pypi/implementation/kant.svg)](https://pypi.python.org/pypi/kant)


A CQRS and Event Sourcing framework for Python 3.

## Installing

```bash
pip install kant
```

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
from kant.aggregates import Aggregate

class BankAccount(Aggregate):
    def apply_bank_account_created(self, event):
        self.id = event.get('id')
        self.owner = event.get('owner')
        self.balance = 0

    def apply_deposit_performed(self, event):
        self.balance += event.get('amount')
```

Now, manage events by EventRepository

```python
# database connection
import aiopg
conn = await aiopg.connect(user='user', password='user', database='database')

# create events
bank_account_created = BankAccountCreated(
    id=123,
    owner='John Doe',
)
deposit_performed = DepositPerformed(
    amount=20,
)

bank_account = BankAccount()
# apply event BankAccountCreated { id: 123, owner: 'John Doe' }
bank_account.dispatch(bank_account_created)
# apply event DepositPerformed { amount: 20 }
bank_account.dispatch(deposit_performed)

async with conn as cursor:
        event_store_repository = EventStoreRepository(cursor)
        event_store_repository.save(
            aggregate_id=bank_account.id,
            events=bank_account.get_events(),
        )
        # get aggregate by id
        stored_events = await event_store_repository.get(123)
        stored_bank_account = BankAccount()
        # apply stored events in stored_bank_account
        stored_bank_account.fetch_events(stored_events)
```

## Features

* Optimistic Concurrency


## Contributing

Please, read the contribute guide [CONTRIBUTING](CONTRIBUTING.md).

## License

**MIT**

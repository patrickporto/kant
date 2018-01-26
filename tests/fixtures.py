from kant.events import models


class BankAccountCreated(models.EventModel):
    id = models.CUIDField(primary_key=True)
    owner = models.CharField()


class DepositPerformed(models.EventModel):
    amount = models.DecimalField()


class OwnerChanged(models.EventModel):
    new_owner = models.CharField()


class WithdrawalPerformed(models.EventModel):
    amount = models.DecimalField()


class FoundAdded(models.EventModel):
    amount = models.DecimalField()


class AccountSchemaModel(models.SchemaModel):
    balance = models.DecimalField()

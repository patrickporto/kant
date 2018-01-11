class BankAccountCreated(object):
    def __init__(self, *, id, owner):
        self.id = id
        self.onwer = owner


class DepositPerformed(object):
    def __init__(self, *, account_id, amount):
        self.account_id = account_id
        self.amount = amount


class OwnerChanged(object):
    def __init__(self, *, account_id, new_owner):
        self.account_id = account_id
        self.new_owner = new_owner


class WithdrawalPerformed(object):
    def __init__(self, *, account_id, amount):
        self.account_id = account_id
        self.amount = amount

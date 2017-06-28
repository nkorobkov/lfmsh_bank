from django.contrib.auth.models import User
from django.db import models
from django.db.models import CASCADE
from django.utils.timezone import now
from bank.models import MoneyType, Transaction
from .AtomicTransaction import AtomicTransaction


class Money(AtomicTransaction):
    receiver = models.ForeignKey(User, related_name='received_money', on_delete=models.CASCADE, null=False)

    type = models.ForeignKey(MoneyType)
    related_transaction = models.ForeignKey(Transaction, on_delete=CASCADE, related_name='related_money_atomics')

    @classmethod
    def new_money(cls, receiver, value, type, description, transaction):
        new_money = cls(related_transaction=transaction, receiver=receiver, value=value, type=type,
                        description=description, counted=False, update_timestamp=now())
        new_money.save()
        return new_money

    def apply(self):
        if self.counted:
            raise AttributeError
        self.related_transaction.creator.account.balance -= self.value
        self.receiver.account.balance += self.value
        self.counted = True

    def undo(self):
        if not self.counted:
            raise AttributeError
        self.related_transaction.creator.account.balance += self.value
        self.receiver.account.balance -= self.value
        self.counted = False
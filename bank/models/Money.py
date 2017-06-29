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

    def __str__(self):
        return "{}@ за {}".format(self.value,self.type)

    def apply(self):
        self._switch_counted(True)

    def undo(self):
        self._switch_counted(False)

    def _switch_counted(self, value):
        if self.counted == value:
            raise AttributeError
        creator = self.related_transaction.creator.account
        receiver = self.receiver.account
        if not value:
            creator.balance += self.value
            receiver.balance -= self.value
        else:
            creator.balance -= self.value
            receiver.balance += self.value
        creator.save()
        receiver.save()
        self.counted = value
        self.update_timestamp = now()
        self.save()
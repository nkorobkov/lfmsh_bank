from django.contrib.auth.models import User
from django.db import models
from django.db.models import CASCADE
from django.utils.timezone import now

from bank.constants import SIGN
from bank.models.MoneyType import MoneyType
from bank.models.Transaction import Transaction
from .AtomicTransaction import AtomicTransaction


class Money(AtomicTransaction):
    receiver = models.ForeignKey(User, related_name='received_money', on_delete=models.CASCADE, null=False)

    type = models.ForeignKey(MoneyType, on_delete=models.PROTECT)
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
        super()._switch_counted(value)
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

    def get_value(self):
        if abs(self.value) > 9.9:
            v = int(self.value)
        else:
            v = round(self.value, 1)
        if v > 0:
            return '+{} {}'.format(str(v), SIGN)
        return '{} {}'.format(str(v), SIGN)

    def to_python(self):
        return {
            "general_group": self.type.readable_group_general,
            "local_group": self.type.readable_group_local,
            "type": self.type.readable_name,
            "value": self.value,
            "receiver": self.receiver.account.long_name(),
            "creator": self.related_transaction.creator.account.long_name(),
            "counted": self.counted,
            "state": self.related_transaction.state.readable_name,
            "description": self.description,
            "update_timestamp": self.update_timestamp.strftime("%d.%m.%Y %H:%M"),
            "creation_timestamp": self.creation_timestamp.strftime("%d.%m.%Y %H:%M")
        }

    def full_info_as_list(self):
        return self.type.full_info_as_list() + \
               super(Money, self).full_info_as_list() + \
               self.receiver.account.full_info_as_list() + \
               self.related_transaction.full_info_as_list()

    def full_info_headers_as_list(self):
        return self.type.full_info_headers_as_list() + \
               super(Money, self).full_info_headers_as_list() + \
               ['receiver_' + x for x in self.receiver.account.full_info_headers_as_list()] + \
               ['transaction_' + x for x in self.related_transaction.full_info_headers_as_list()]

from django.db import models
from django.contrib.auth.models import User
from django.db.models import CASCADE
from django.utils.timezone import now

from bank.constants import *
from bank.models import Transaction
from . import TransactionState


class AtomicTransaction(models.Model):
    update_timestamp = models.DateTimeField(blank=True, null=True)
    creation_timestamp = models.DateTimeField(auto_now_add=True)

    description = models.TextField(max_length=1023, blank=True)
    value = models.FloatField(default=0)
    counted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def _switch_counted(self, value):
        if self.counted == value:
            raise AttributeError
        self.counted = value
        self.update_timestamp = now()
        self.save()

    def get_creation_timestamp(self):
        return self.creation_timestamp.strftime("%d.%m.%Y %H:%M")


'''
    @classmethod
    def create_trans(cls, recipient, value, creator, description, type, status):

        if type.group1 == 'fine' or type.group1 == 'payment':
            value = - value

        new_trans = cls(recipient=recipient, value=value, creator=creator, description=description,
                        type=type, status=status)

        if status.name == 'PR' and recipient != None:
            a = new_trans.count()
            if a:
                new_trans.do_counters(1)
        else:
            new_trans.save()

        return new_trans

    def count(self):

        if self.counted:
            return False

        if self.type.group1 != 'attend':
            a = self.recipient.account
            a.balance = a.balance + self.value
            a.save()

            a = self.creator.account
            a.balance = a.balance - self.value
            a.save()
        else:
            # return false if attend is imposible
            if Transaction.objects.filter(recipient=self.recipient).filter(
                    value__in=[((int(self.value) // 100) * 100 + a) for a in
                               SF_IMPOSIBLE[int(self.value) % 100]]).filter(counted=True):
                return False

        self.counted = True
        self.save()
        return True

    def do_counters(self, value):

        if self.type.name == 'fac_pass':
            a = self.recipient.account
            a.fac_passed += value
            a.save()

        if self.type.group1 == 'attend' and self.type.name != 'lec_attend':
            a = self.recipient.account
            a.sem_fac_attend += value
            a.save()

        if self.type.name == 'lab_pass':
            a = self.recipient.account
            a.lab_passed += value
            a.save()

        if self.type.name == 'fine_lec':
            a = self.recipient.account
            a.lec_missed += value
            a.save()
        if self.type.name == 'sem':
            a = self.recipient.account
            a.sem_read += value
            a.save()

    def cancel(self):

        if not self.counted:
            return False

        if self.type.group1 != 'attend':
            a = self.recipient.account
            a.balance = a.balance - self.value
            a.save()

            a = self.creator.account
            a.balance = a.balance + self.value
            a.save()
        else:
            if len(Transaction.objects.filter(value=self.value).filter(recipient=self.recipient).filter(
                    counted=True)) != 1:
                self.counted = False
                self.save()
                return False

        self.do_counters(-1)
        self.counted = False
        self.save()

        return True

    def can_be_declined(self):
        if self.status.name in ['DA', 'DC']:
            return False
        if self.type.name == 'p2p' and self.status.name == 'PR':
            return False
        print(self.meta.all())
        print(len(self.meta.all()))
        if len(self.meta.all()) != 0:
            return False

        return True

    def get_creation_date(self):
        return self.creation_date.strftime("%d.%m.%Y %H:%M")

    def get_value(self):
        if abs(self.value) > 9.9:
            return int(self.value)
        return round(self.value, 1)

    def get_value_as_date(self):
        year = 2000 + int(self.value) // 1000000
        month = (int(self.value) // 10000) % 100
        day = (int(self.value) // 100) % 100
        block = (int(self.value)) % 10
        if (int(self.value) // 10) % 10 == SEM_IND:
            if (int(self.value)) % 10 == 0:
                return str('Лекция', 'utf-8')
            return str('{0}.{1}.{2}, {3} блок семинаров'.format(year, month, day, block), 'utf-8')
        return str('{0}.{1}.{2}, {3} блок факультативов'.format(year, month, day, block), 'utf-8')```
'''

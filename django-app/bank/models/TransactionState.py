from django.db import models

from bank.models.AbstractType import AbstractType


class TransactionState(AbstractType):
    counted = models.BooleanField(default=False)
    possible_transitions = models.ManyToManyField('self', symmetrical=False)




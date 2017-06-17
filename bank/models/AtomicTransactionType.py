from django.db import models
from django.db.models import CASCADE

from bank.models.AbstractType import AbstractType


class AtomicTransactionType(AbstractType):
    group_general = models.CharField(max_length=31, blank=True, null=True)
    group_local = models.CharField(max_length=31, blank=True, null=True)
    readable_group_local = models.CharField(max_length=127, default='Other')
    readable_group_general = models.CharField(max_length=127, default='Other')

class Meta:
    abstract = True

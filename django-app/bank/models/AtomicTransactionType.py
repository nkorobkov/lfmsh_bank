from django.db import models
from django.db.models import CASCADE

from bank.models.AbstractType import AbstractType


class AtomicTransactionType(AbstractType):
    group_general = models.CharField(max_length=31, blank=True, null=True)
    group_local = models.CharField(max_length=31, blank=True, null=True)
    readable_group_local = models.CharField(max_length=127, default='Other')
    readable_group_general = models.CharField(max_length=127, default='Other')

    def full_info_as_list(self):
        return [
                   self.readable_group_general,
                   self.readable_group_local
               ] + super(AtomicTransactionType, self).full_info_as_list()

    def full_info_headers_as_list(self):
        return [
                   'type_group_general',
                   'type_group_local'
               ] + super(AtomicTransactionType, self).full_info_headers_as_list()


class Meta:
    abstract = True

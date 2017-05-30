
from django.db import models
from .Transaction import Transaction


class MetaTransaction(models.Model):
    creation_dict = models.CharField(max_length=20000)

    transactions = models.ManyToManyField(Transaction, default=None, blank=True, related_name='meta')
    meta = models.ForeignKey(Transaction, null=True, related_name='meta_link')

from django.contrib.auth.models import User
from django.db import models

from bank.models import TransactionType, TransactionState


class Transaction(models.Model):
    creator = models.ForeignKey(User, related_name='created_transactions', on_delete=models.PROTECT, null=False)
    creation_map = models.CharField(max_length=262143)
    type = models.ForeignKey(TransactionType, on_delete=models.PROTECT, null=False)
    state = models.ForeignKey(TransactionState)


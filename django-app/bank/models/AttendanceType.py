from django.db import models
from django.db.models import CASCADE

from .AtomicTransactionType import AtomicTransactionType


class AttendanceType(AtomicTransactionType):
    related_transaction_type = models.ForeignKey('TransactionType', on_delete=CASCADE,
                                                 related_name='related_attendance', null=True)

    pass

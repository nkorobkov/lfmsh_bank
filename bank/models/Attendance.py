from django.contrib.auth.models import User
from django.db import models
from django.db.models import CASCADE

from bank.models import Transaction
from .AtomicTransaction import AtomicTransaction
from .AttendanceType import AttendanceType


class Attendance(AtomicTransaction):
    receiver = models.ForeignKey(User, related_name='received_attendance', on_delete=models.CASCADE, null=False)

    type = models.ForeignKey(AttendanceType)
    attendance_block_name = models.CharField(max_length=63)
    related_transaction = models.ForeignKey(Transaction, on_delete=CASCADE, related_name='related_attendance_atomics')


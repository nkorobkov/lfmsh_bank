from django.contrib.auth.models import User
from django.db import models
from django.db.models import CASCADE, SET_NULL
from django.utils.timezone import now

from bank.models import Transaction, AttendanceBlock
from .AtomicTransaction import AtomicTransaction
from .AttendanceType import AttendanceType


class Attendance(AtomicTransaction):
    receiver = models.ForeignKey(User, related_name='received_attendance', on_delete=models.CASCADE, null=False)

    type = models.ForeignKey(AttendanceType)
    attendance_block_name = models.ForeignKey(AttendanceBlock, on_delete=SET_NULL, null=True,
                                              related_name='attendances')
    related_transaction = models.ForeignKey(Transaction, on_delete=CASCADE, related_name='related_attendance_atomics')

    @classmethod
    def new_attendance(cls, receiver, value, type, description, attendance_block_name, transaction):
        new_att = cls(related_transaction=transaction, receiver=receiver, value=value, type=type,
                      description=description, counted=False, update_timestamp=now(),
                      attendance_block_name=attendance_block_name)
        new_att.save()
        return new_att

    def apply(self):
        self._switch_counted(True)

    def undo(self):
        self._switch_counted(False)

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
    attendance_block = models.ForeignKey(AttendanceBlock, on_delete=SET_NULL, null=True,
                                              related_name='attendances')
    date = models.DateField()
    related_transaction = models.ForeignKey(Transaction, on_delete=CASCADE, related_name='related_attendance_atomics')

    @classmethod
    def new_attendance(cls, receiver, value, type, description, date, transaction,  attendance_block_name=None):
        attendance_block = AttendanceBlock.objects.get(name=attendance_block_name) if attendance_block_name else None
        new_att = cls(related_transaction=transaction, receiver=receiver, value=value, type=type,
                      description=description, counted=False, update_timestamp=now(), date=date,
                      attendance_block=attendance_block)
        new_att.save()
        return new_att

    def apply(self):
        if self.is_valid():
            self._switch_counted(True)

    def undo(self):
        self._switch_counted(False)

    def is_valid(self):
        if not self.attendance_block:
            return True
        for suspicious in Attendance.objects.filter(receiver=self.receiver).filter(date=self.date).filter(counted=True).exclude(id=self.id).all():
            if self.attendance_block.clashes_with(suspicious.attendance_block):
                return False
        return True

    def get_counted(self):
        return "Засчитан" if self.counted else "Не засчитан"

    def get_date(self):
        return self.date.strftime("%d.%m")

    def __str__(self):
        return "{} {} {} {}".format(str(self.attendance_block), str(self.receiver ), str(self.date ), str(self.counted))

    def to_python(self):
        return {
            "type": self.type.readable_name,
            "value": self.value,
            "receiver": self.receiver.account.long_name(),
            "counted": self.counted,
            "description": self.description,
            "update_timestamp": self.update_timestamp.strftime("%d.%m.%Y %H:%M"),
            "creation_timestamp": self.creation_timestamp.strftime("%d.%m.%Y %H:%M"),
            "attendance_block": self.attendance_block.readable_name if self.attendance_block else "null",
            "date": self.date.strftime("%d.%m"),

        }
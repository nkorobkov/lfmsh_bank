from bank.models import AttendanceType
from bank.models.AbstractType import AbstractType
from django.db import models


class AttendanceBlock(AbstractType):
    start_time = models.TimeField()
    end_time = models.TimeField()
    related_attendance_types = models.ManyToManyField(AttendanceType, related_name="related_attendance_blocks")

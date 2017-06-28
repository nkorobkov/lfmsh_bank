from bank.models.AbstractType import AbstractType
from django.db import models


class AttendanceBlock(AbstractType):
    start_time = models.TimeField()
    end_time = models.TimeField()

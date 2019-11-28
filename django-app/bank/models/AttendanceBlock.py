from bank.models.AttendanceType import AttendanceType
from bank.models.AbstractType import AbstractType
from django.db import models


class AttendanceBlock(AbstractType):
    start_time = models.TimeField()
    end_time = models.TimeField()
    related_attendance_types = models.ManyToManyField(AttendanceType, related_name="related_attendance_blocks")

    def clashes_with(self, other_block):
        if other_block:
            if (other_block.start_time <= self.start_time and self.start_time  < other_block.end_time) or (other_block.start_time < self.end_time and self.end_time <= other_block.end_time):
                return True
        return False
from django.db import models
from django.contrib.auth.models import User
from bank import helper_functions as hf
from bank.constants import *

'''
Extention of a User Class
'''


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    balance = models.FloatField(default=0)
    middle_name = models.CharField(max_length=40, default='Not stated')

    party = models.IntegerField(default=0)
    grade = models.IntegerField(blank=True, default=0)

    '''
    def times_attended(self, attendance):
        attendance = Attendance.objects.filter(receiver=self.user, type__name=attendance.value)
        return sum([a.value for a in attendance])
    '''

    def get_penalty(self):
        p = 0
        p += max(0, (self.lab_needed() - int(self.lab_passed))) * LAB_PENALTY  # labs
        p += hf.sem_fac_penalty(max(0, (hf.sem_needed - int(self.sem_fac_attend))))  # semfac attend
        p += SEM_NOT_READ_PEN * max(0, 1 - int(self.sem_read))
        return p

    def __str__(self):
        if self.user.first_name:

            return self.user.last_name + ' ' + self.user.first_name[0] + '. ' + self.middle_name[0] + '.'
        else:
            return self.user.last_name

    def long_name(self):
        return self.user.last_name + ' ' + self.user.first_name + ' ' + self.middle_name

    def short_name(self):
        if self.user.first_name:

            return self.user.last_name + ' ' + self.user.first_name[0] + '. ' + self.middle_name[0] + '.'
        else:
            return self.user.last_name

    '''def lab_needed(self):
        return constants.lab_pass_needed[self.grade]

    def fac_needed(self):
        return constants.fac_pass_needed[self.grade]

    def sem_att_needed(self):
        return constants.sem_needed

    def sem_att_w(self):
        print(100 * int(self.sem_fac_attend) / self.sem_att_needed())
        return (100 * int(self.sem_fac_attend) / self.sem_att_needed())

    def lab_passed_w(self):

        print(100 * int(self.lab_passed) / self.lab_needed())
        return (100 * int(self.lab_passed) / self.lab_needed())

    def fac_passed_w(self):
        if self.fac_needed():
            print(100 * int(self.fac_passed) / self.fac_needed())
            return (100 * int(self.fac_passed) / self.fac_needed())

    def sem_read_w(self):

        return int(self.sem_read) * 100'''

    def get_balance(self):
        if abs(self.balance) > 9.99:
            return int(self.balance)
        return round(self.balance, 1)

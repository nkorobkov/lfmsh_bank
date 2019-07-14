import itertools
from django.db import models
from django.contrib.auth.models import User
from bank.constants import SIGN, SEM_NOT_READ_PEN, AttendanceTypeEnum, LAB_PENALTY, STEP_OBL_STD, \
    INITIAL_STEP_OBL_STD, LAB_PASS_NEEDED, OBL_STUDY_NEEDED, FAC_PASS_NEEDED, FAC_PENALTY, \
    LECTURE_PENALTY_STEP, LECTURE_PENALTY_INITIAL

'''
Extention of a User Class
'''


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    balance = models.FloatField(default=0)
    middle_name = models.CharField(max_length=40, default='Not stated')

    party = models.IntegerField(default=0)
    grade = models.IntegerField(blank=True, default=0)

    def get_counter(self, counter_name):
        return int(
            sum([a.value for a in self.user.received_attendance.filter(type__name=counter_name).filter(counted=True)]))

    def __str__(self):
        return self.short_name() + self.get_balance() if self.balance else ""

    def name_with_balance(self):
        return '{} {} {}'.format(self.user.last_name, self.user.first_name, self.get_balance())

    def long_name(self):
        return self.user.last_name + ' ' + self.user.first_name

    def short_name(self):
        if len(self.user.first_name) > 0 and len(self.user.account.middle_name) > 0:
            return self.user.last_name + ' ' + self.user.first_name[0] + '. ' + self.middle_name[0] + '.'
        else:
            return self.user.last_name

    def get_balance(self):
        if abs(self.balance) > 9.99:
            return '{}{}'.format(str(int(self.balance)), SIGN)
        return '{}{}'.format(str(round(self.balance, 1)), SIGN)

    def get_all_money(self):
        a = list(self.user.received_money.all()) + list(itertools.chain(
            *[list(t.related_money_atomics.all()) for t in self.user.created_transactions.all()]))

        a.sort(key=lambda t: t.creation_timestamp)
        return a

    def get_final_study_fine(self):
        """
        There is four major things you can be charged for
        1. not making a seminar
        2. Not attending enough obligatory studies (sem_attend, fac_attend)
        3. Not passing enough labs
        4. Not passing enough facs

        :return: positive value of fine
        """
        fine = 0
        fine += self.get_sem_fine()
        fine += self.get_obl_study_fine()
        fine += self.get_lab_fine()
        fine += self.get_fac_fine()

        return fine

    def get_sem_fine(self):
        return SEM_NOT_READ_PEN * max(0, 1 - int(self.get_counter(AttendanceTypeEnum.seminar_pass.value)))

    def get_lab_fine(self):
        return max(0, (self.lab_needed() - int(self.get_counter(AttendanceTypeEnum.lab_pass.value)))) * LAB_PENALTY

    def get_obl_study_fine(self):
        deficit = max(0, (OBL_STUDY_NEEDED - int(
            self.get_counter(AttendanceTypeEnum.seminar_attend.value) + self.get_counter(
                AttendanceTypeEnum.fac_attend.value))))
        single_fine = INITIAL_STEP_OBL_STD
        fine = 0
        for i in range(deficit):
            fine += single_fine
            single_fine += STEP_OBL_STD
        return fine

    def get_fac_fine(self):
        return max(0, (self.fac_needed() - int(self.get_counter(AttendanceTypeEnum.fac_pass.value)))) * FAC_PENALTY

    def lab_needed(self):
        return LAB_PASS_NEEDED[self.grade]

    def fac_needed(self):
        return FAC_PASS_NEEDED[self.grade]

    def get_next_missed_lec_penalty(self):
        return (
                   self.get_counter(
                       AttendanceTypeEnum.lecture_miss.value)) * LECTURE_PENALTY_STEP + LECTURE_PENALTY_INITIAL

    def full_info_as_list(self):
        return [
            self.user.first_name,
            self.user.last_name,
            self.middle_name,
            self.user.username,
            self.party,
            self.grade,
            self.balance
        ]

    def full_info_as_map(self, with_balance=True):
        m = {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'middle_name': self.middle_name,
            'username': self.user.username,
            'party': self.party,
            'grade': self.grade,
        }
        if with_balance:
            m['balance'] = self.balance
        return m

    def full_info_headers_as_list(self):
        return [
            'first_name',
            'last_name',
            'middle_name',
            'username',
            'party',
            'grade',
            'balance'
        ]

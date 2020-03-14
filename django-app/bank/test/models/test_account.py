from django.contrib.auth.models import User
from django.test import TestCase

from bank.constants import States
from bank.constants.constants import *
from bank.constants.TransactionTypeEnum import *

from bank.constants.AttendanceTypeEnum import *

from bank.models.TransactionType import TransactionType
from bank.models.TransactionState import TransactionState
from bank.models.Attendance import Attendance
from bank.models.AttendanceType import AttendanceType
from bank.models.Transaction import Transaction
from bank.models.Account import Account




class AccountTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(first_name='First', last_name='Last', username='user',
                                        password='1234')
        user.save()
        Account.objects.create(user=user, middle_name='Middle', grade=10, party=1)

        user2 = User.objects.create_user(first_name='First2', last_name='Last2', username='user2',
                                         password='1234')
        user2.save()
        Account.objects.create(user=user2, middle_name='Middle2', grade=10, party=1)

    def test_basic_acc_created(self):
        account = Account.objects.get(party=1, middle_name='Middle')
        self.assertEqual(account.middle_name, 'Middle')
        self.assertEqual(account.grade, 10)
        self.assertEqual(account.party, 1)
        self.assertEqual(account.user.first_name, 'First')
        self.assertEqual(account.user.username, 'user')
        self.assertEqual(account.balance, 0)

    def test_study_fine_calc(self):
        account = Account.objects.get(party=1, middle_name='Middle')

        single_fac_fine = FAC_PENALTY
        lab_fine = LAB_PASS_NEEDED[account.grade] * LAB_PENALTY
        # arithmetic progression
        obl_fine = (INITIAL_STEP_OBL_STD * 2 + ((OBL_STUDY_NEEDED - 1) * STEP_OBL_STD)) * OBL_STUDY_NEEDED / 2
        sem_fine = SEM_NOT_READ_PEN

        fine_with_zero_activity = single_fac_fine + lab_fine + obl_fine + sem_fine

        self.assertEqual(account.get_obl_study_fine(), obl_fine)
        self.assertEqual(account.get_sem_fine(), sem_fine)
        self.assertEqual(account.get_lab_fine(), lab_fine)
        self.assertEqual(account.get_fac_fine(), single_fac_fine)

        self.assertEqual(account.get_final_study_fine(), fine_with_zero_activity)

    def test_study_fine_calc_with_activity(self):
        account = Account.objects.get(party=1, middle_name='Middle')

        single_fac_fine = FAC_PENALTY
        lab_fine = LAB_PASS_NEEDED[account.grade] * LAB_PENALTY
        # arithmetic progression
        obl_fine = (INITIAL_STEP_OBL_STD * 2 + ((OBL_STUDY_NEEDED - 2) * STEP_OBL_STD)) * (OBL_STUDY_NEEDED-1) / 2
        sem_fine = SEM_NOT_READ_PEN

        user2 = User.objects.get(username='user2')
        user = User.objects.get(username='user')

        TransactionState.objects.create(name=States.created.value)
        TransactionType.objects.create(name=TransactionTypeEnum.seminar.value)
        AttendanceType.objects.create(name=AttendanceTypeEnum.seminar_attend.value)


        transaction = Transaction.new_transaction(user2,
                                                  TransactionType.objects.get(name=TransactionTypeEnum.seminar.value),
                                                  {})
        attendance = Attendance.new_attendance(user, 1,
                                               AttendanceType.objects.get(name=AttendanceTypeEnum.seminar_attend.value),
                                               'desc', '1111-11-11', transaction)
        attendance.counted = True
        attendance.save()

        fine_with_zero_activity = single_fac_fine + lab_fine + obl_fine + sem_fine

        self.assertEqual(account.get_obl_study_fine(), obl_fine)
        self.assertEqual(account.get_sem_fine(), sem_fine)
        self.assertEqual(account.get_lab_fine(), lab_fine)
        self.assertEqual(account.get_fac_fine(), single_fac_fine)

        self.assertEqual(account.get_final_study_fine(), fine_with_zero_activity)

from django.contrib.auth.models import User
from django.test import TestCase

from bank.models.Attendance import Attendance
from bank.models.Transaction import Transaction
from bank.models.Account import Account
from bank.models.AttendanceType import AttendanceType
from bank.models.TransactionType import TransactionType
from bank.models.AttendanceBlock import AttendanceBlock

from bank.test.seeder import seed_db
from bank.constants import TransactionTypeEnum, AttendanceTypeEnum


class AttendanceTestCase(TestCase):

  @classmethod
  def setUpClass(cls):
    seed_db()

  @classmethod
  def tearDownClass(cls):
    # Django tests fail if we don't add this empty method
    pass

  def setUp(self):
    user_creator = User.objects.create_user(
        first_name='Creator',
        last_name='Last',
        username='creator',
        password='1234')
    user_creator.save()
    Account.objects.create(
        user=user_creator, middle_name='Middle', grade=10, party=1)

    user_receiver = User.objects.create_user(
        first_name='Receiver',
        last_name='Last',
        username='receiver',
        password='1234')
    user_receiver.save()
    Account.objects.create(
        user=user_receiver, middle_name='Middle', grade=10, party=1)

    AttendanceBlock.objects.create(
        name='10-11', start_time='10:00:00', end_time='11:00:00')
    AttendanceBlock.objects.create(
        name='10-12', start_time='10:00:00', end_time='12:00:00')
    AttendanceBlock.objects.create(
        name='11-12', start_time='11:00:00', end_time='12:00:00')
    AttendanceBlock.objects.create(
        name='11-13', start_time='11:00:00', end_time='13:00:00')

    self.creator = user_creator
    self.receiver = user_receiver
    self.att_type = AttendanceType.objects.get(
        name=AttendanceTypeEnum.seminar_attend.value)
    transaction_type = \
      TransactionType.objects.get(name=TransactionTypeEnum.seminar.value)
    self.transaction = Transaction.new_transaction(self.creator,
                                                   transaction_type, {})

  def test_is_valid_returns_true(self):

    attendance = Attendance.new_attendance(self.receiver, 1, self.att_type,
                                           'description', '2020-01-01',
                                           self.transaction, '10-11')

    other_date = Attendance.new_attendance(self.receiver, 1, self.att_type,
                                           'description', '2020-01-02',
                                           self.transaction, '10-11')

    other_time = Attendance.new_attendance(self.receiver, 1, self.att_type,
                                           'description', '2020-01-01',
                                           self.transaction, '11-12')

    other_user = Attendance.new_attendance(self.creator, 1, self.att_type,
                                           'description', '2020-01-01',
                                           self.transaction, '10-11')

    other_date.apply()
    other_time.apply()
    other_user.apply()

    self.assertTrue(other_date.counted)
    self.assertTrue(other_time.counted)
    self.assertTrue(other_user.counted)

    self.assertTrue(attendance.is_valid())

  def test_is_valid_catches_clashes_properly(self):
    attendance = Attendance.new_attendance(self.receiver, 1, self.att_type,
                                           'description', '2020-01-01',
                                           self.transaction, '10-12')

    colapsing = Attendance.new_attendance(self.receiver, 1, self.att_type,
                                          'description', '2020-01-01',
                                          self.transaction, '11-13')

    colapsing.apply()

    self.assertFalse(attendance.is_valid())
    self.assertTrue(colapsing.is_valid())

    colapsing.undo()

    self.assertTrue(attendance.is_valid())

  def test_applies_when_no_clash(self):

    attendance = Attendance.new_attendance(self.receiver, 1, self.att_type,
                                           'description', '2020-01-01',
                                           self.transaction, '10-12')

    colapsing = Attendance.new_attendance(self.receiver, 1, self.att_type,
                                          'description', '2020-01-01',
                                          self.transaction, '11-13')

    self.assertFalse(colapsing.counted)
    self.assertFalse(attendance.counted)

    attendance.apply()

    self.assertTrue(attendance.counted)

  def test_not_applies_when_clash(self):

    attendance = Attendance.new_attendance(self.receiver, 1, self.att_type,
                                           'description', '2020-01-01',
                                           self.transaction, '10-12')

    colapsing = Attendance.new_attendance(self.receiver, 1, self.att_type,
                                          'description', '2020-01-01',
                                          self.transaction, '11-13')

    attendance.apply()
    colapsing.apply()
    self.assertTrue(attendance.counted)
    self.assertFalse(colapsing.counted)

  def test_changes_states_properly(self):
    attendance = Attendance.new_attendance(self.receiver, 1, self.att_type,
                                           'description', '2020-01-01',
                                           self.transaction, '10-12')

    attendance.apply()
    self.assertTrue(attendance.counted)
    attendance.undo()
    self.assertFalse(attendance.counted)
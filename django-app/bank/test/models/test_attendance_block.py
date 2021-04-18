from django.test import TestCase
from bank.models.AttendanceBlock import AttendanceBlock

from bank.test.seeder import seed_db


class AttendanceBlockTestCase(TestCase):

  @classmethod
  def setUpClass(cls):
    seed_db()

  @classmethod
  def tearDownClass(cls):
    # Django tests fail if we don't add this empty method
    pass

  def test_seeder_worked(self):
    block = AttendanceBlock.objects.get(name='seminar_1')
    self.assertEqual(block.readable_name, 'Первый блок семинаров')

  def test_non_same_time_blocks_do_not_clash(self):
    first = AttendanceBlock.objects.create(
        name='first',
        readable_name='first',
        start_time='11:00:00',
        end_time='12:00:00'
    )
    second = AttendanceBlock.objects.create(
        name='second',
        readable_name='second',
        start_time='13:00:00',
        end_time='14:00:00'
    )
    self.assertFalse(first.clashes_with(second))
    self.assertFalse(second.clashes_with(first))

  def test_intersecting_blocks_do_clash(self):
    first = AttendanceBlock.objects.create(
        name='first',
        readable_name='first',
        start_time='11:00:00',
        end_time='13:00:00'
    )
    second = AttendanceBlock.objects.create(
        name='second',
        readable_name='second',
        start_time='12:00:00',
        end_time='14:00:00'
    )
    self.assertTrue(first.clashes_with(second))
    self.assertTrue(second.clashes_with(first))

  def test_back_to_back_blocks_do_not_clash(self):
    first = AttendanceBlock.objects.create(
        name='first',
        readable_name='first',
        start_time='11:00:00',
        end_time='12:00:00'
    )
    second = AttendanceBlock.objects.create(
        name='second',
        readable_name='second',
        start_time='12:00:00',
        end_time='14:00:00'
    )
    self.assertFalse(first.clashes_with(second))
    self.assertFalse(second.clashes_with(first))

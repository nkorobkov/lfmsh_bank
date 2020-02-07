from django.test import TestCase
from bank.models.AttendanceBlock import AttendanceBlock

from bank.test.seeder import seed_db


class AttendanceBlockTestCase(TestCase):
    def setUp(self):
        print('seeding db for attendance block tests')
        seed_db()

    def test_seeder_worked(self):
        block = AttendanceBlock.objects.get(name='seminar_1')
        self.assertEqual(block.readable_name, 'Первый блок семинаров')


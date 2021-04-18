from django.test import SimpleTestCase
from bank.helper_functions import get_perm_name


class TestPermName(SimpleTestCase):

  def test_one_arg(self):
    self.assertEqual('bank.a', get_perm_name('a'))

  def test_multiple_args(self):
    self.assertEqual('bank.a_b', get_perm_name('a', 'b'))

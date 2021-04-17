from django.contrib.auth.models import User
from django.test import TestCase

from bank.models.Money import Money
from bank.models.Transaction import Transaction
from bank.models.Account import Account
from bank.models.MoneyType import MoneyType
from bank.models.TransactionType import TransactionType
from bank.test.seeder import seed_db
from bank.constants import TransactionTypeEnum, MoneyTypeEnum



class MoneyTestCase(TestCase):

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

  def test_apply_changes_balances(self):
    creator = User.objects.get(username='creator')
    receiver = User.objects.get(username='receiver')
    creator_balance = creator.account.balance
    receiver_balance = receiver.account.balance
    money_type = MoneyType.objects.get(name=MoneyTypeEnum.radio_help.value)
    transaction_type = \
      TransactionType.objects.get(name=TransactionTypeEnum.seminar.value)
    transaction = Transaction.new_transaction(creator, transaction_type, {})

    money = Money.new_money(receiver, 10, money_type, 'description',
                            transaction)

    money.apply()

    self.assertEqual(creator.account.balance, creator_balance - 10)
    self.assertEqual(receiver.account.balance, receiver_balance + 10)

  def test_apply_twice_raises(self):
    creator = User.objects.get(username='creator')
    receiver = User.objects.get(username='receiver')
    money_type = MoneyType.objects.get(name=MoneyTypeEnum.radio_help.value)
    transaction_type = \
      TransactionType.objects.get(name=TransactionTypeEnum.seminar.value)
    transaction = Transaction.new_transaction(creator, transaction_type, {})

    money = Money.new_money(receiver, 10, money_type, 'description',
                            transaction)
    money.apply()
    with self.assertRaises(AttributeError):
      money.apply()

  def test_undo_changes_ballances(self):
    creator = User.objects.get(username='creator')
    receiver = User.objects.get(username='receiver')
    creator_balance = creator.account.balance
    receiver_balance = receiver.account.balance
    money_type = MoneyType.objects.get(name=MoneyTypeEnum.radio_help.value)
    transaction_type = \
      TransactionType.objects.get(name=TransactionTypeEnum.seminar.value)
    transaction = Transaction.new_transaction(creator, transaction_type, {})

    money = Money.new_money(receiver, 10, money_type, 'description',
                            transaction)
    money.apply()
    money.undo()
    self.assertEqual(creator.account.balance, creator_balance)
    self.assertEqual(receiver.account.balance, receiver_balance)

  def test_undo_non_applied_transaction_raises(self):
    creator = User.objects.get(username='creator')
    receiver = User.objects.get(username='receiver')
    money_type = MoneyType.objects.get(name=MoneyTypeEnum.radio_help.value)
    transaction_type = \
      TransactionType.objects.get(name=TransactionTypeEnum.seminar.value)
    transaction = Transaction.new_transaction(creator, transaction_type, {})

    money = Money.new_money(receiver, 10, money_type, 'description',
                            transaction)
    with self.assertRaises(AttributeError):
      money.undo()

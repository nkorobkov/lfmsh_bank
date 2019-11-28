from django.contrib.auth.models import User
from django.core.management import BaseCommand

from bank.constants import UserGroups, BANKIR_USERNAME, TransactionTypeEnum, MoneyTypeEnum
from bank.helper_functions import get_session_day, get_tax_from_session_day
from bank.models.Money import Money
from bank.models.TransactionType import TransactionType
from bank.models.MoneyType import MoneyType
from bank.models.Transaction import Transaction

class Command(BaseCommand):
    args = 'No args'
    help = 'charge tax from students'

    def handle(self, *args, **options):
        self.charge_tax()

    @staticmethod
    def charge_tax():
        day = get_session_day()
        tax_value = get_tax_from_session_day(day)
        print("Current day {}, tax: {}".format(day, tax_value))
        if tax_value <= 0:
            print('Tax is < 0 transactions not created')
            return
        creator = User.objects.get(username=BANKIR_USERNAME)
        t_type = TransactionType.objects.get(name=TransactionTypeEnum.tax.value)
        money_type = MoneyType.objects.get(name=MoneyTypeEnum.tax.value)
        new_transaction = Transaction.new_transaction(creator, t_type, {})
        for student in User.objects.filter(groups__name=UserGroups.student.value):
            Money.new_money(student, -tax_value, money_type, "", new_transaction)
        new_transaction.process()
        for ad in new_transaction.related_money_atomics.all():
            print(ad.receiver.account.long_name(), ad.receiver.account.get_balance())

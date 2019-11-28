from django.contrib.auth.models import User

from bank.constants import MoneyTypeEnum, TransactionTypeEnum
from bank.controls.transaction_controllers.TableTransactionController import TableTransactionController
from bank.forms import FineKernelForm
from bank.models.Money import Money
from bank.models.TransactionType import TransactionType
from bank.models.MoneyType import MoneyType
from bank.models.Transaction import Transaction

class FineTransactionController(TableTransactionController):
    template_url = 'bank/add/add_fine.html'
    value_show_name = 'Штраф'
    header = "Штраф"

    @staticmethod
    def _get_kernel_form():
        return FineKernelForm


    @staticmethod
    def get_initial_form_data(creator_username):
        initial = super(FineTransactionController, FineTransactionController).get_initial_form_data(
            creator_username)
        for in_data in initial:
            in_data['money_type'] = MoneyTypeEnum.fine_any.value
        return initial


    @staticmethod
    def get_transaction_from_form_data(formset_data, update_of):

        first_form = formset_data[0]
        creator = User.objects.get(username=first_form['creator_username'])

        new_transaction = Transaction.new_transaction(creator, TransactionType.objects.get(name=TransactionTypeEnum.fine.value),
                                                      formset_data, update_of)
        money_type = MoneyType.objects.get(name=first_form['money_type'])

        for atomic_data in formset_data:
            value = atomic_data['value']
            if value:
                value = - value
                receiver = User.objects.get(username=atomic_data['receiver_username'])
                Money.new_money(receiver, value,
                                money_type,
                                first_form['description'],
                                new_transaction)
        return new_transaction

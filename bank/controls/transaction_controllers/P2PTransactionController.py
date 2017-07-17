from django.contrib.auth.models import User
from django.forms import formset_factory

from bank.constants import MoneyTypeEnum, TransactionTypeEnum
from bank.controls.transaction_controllers.TransactionController import TransactionController
from bank.forms import P2PKernelForm
from bank.models import Transaction, MoneyType, Money, TransactionType


class P2PTransactionController(TransactionController):
    template_url = 'bank/add/add_p2p.html'

    @staticmethod
    def get_blank_form():
        p2p_formset = formset_factory(P2PKernelForm, max_num=1)
        return p2p_formset

    @staticmethod
    def get_initial_form_data(creator_username):
        return [{'receiver_username': None, 'creator_username': creator_username, 'description': ''}]

    @staticmethod
    def get_transaction_from_form_data(formset_data, update_of):

        first_form = formset_data[0]
        creator = User.objects.get(username=first_form['creator_username'])

        new_transaction = Transaction.new_transaction(creator, TransactionType.objects.get(name=TransactionTypeEnum.p2p.value),
                                                      formset_data, update_of)
        receiver = User.objects.get(username=first_form['receiver_username'])
        Money.new_money(receiver, first_form['value'],
                        MoneyType.objects.get(name=MoneyTypeEnum.p2p.value),
                        first_form['description'],
                        new_transaction)
        return new_transaction

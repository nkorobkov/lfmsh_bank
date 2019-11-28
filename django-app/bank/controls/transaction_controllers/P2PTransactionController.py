from functools import partial, wraps

from django.contrib.auth.models import User
from django.forms import formset_factory

from bank.constants import MoneyTypeEnum, TransactionTypeEnum
from bank.constants.BankAPIExeptions import P2PIllegalAmount, SelfMoneyTransfer, EmptyDescriptionError, UserDoesNotExist
from bank.controls.transaction_controllers.TransactionController import TransactionController
from bank.forms import P2PKernelForm
from bank.models.Money import Money
from bank.models.MoneyType import MoneyType
from bank.models.Transaction import Transaction
from bank.models.TransactionType import TransactionType



class P2PTransactionController(TransactionController):
    template_url = 'bank/add/add_p2p.html'

    @classmethod
    def get_blank_form(cls, creator_username):
        p2p_formset = formset_factory(
            wraps(P2PKernelForm)(partial(P2PKernelForm, creator=User.objects.get(username=creator_username))),
            max_num=1)
        return p2p_formset

    @staticmethod
    def get_initial_form_data(creator_username):
        return [{'receiver_username': None, 'creator_username': creator_username, 'description': ''}]

    @staticmethod
    def get_transaction_from_form_data(formset_data, update_of):
        first_form = formset_data[0]
        creator = User.objects.get(username=first_form['creator_username'])

        new_transaction = Transaction.new_transaction(creator,
                                                      TransactionType.objects.get(name=TransactionTypeEnum.p2p.value),
                                                      formset_data, update_of)
        receiver = User.objects.get(username=first_form['receiver_username'])
        Money.new_money(receiver, first_form['value'],
                        MoneyType.objects.get(name=MoneyTypeEnum.p2p.value),
                        first_form['description'],
                        new_transaction)
        return new_transaction

    @staticmethod
    def build_transaction_from_api_request(api_request_body):
        creator = User.objects.get(username=api_request_body.get('creator'))
        receiver_username = api_request_body.get('money')[0].get('receiver')
        value = api_request_body.get('money')[0].get('value')
        description = api_request_body.get('description')
        formset_data = [
            {'value': value,
             'receiver_username': receiver_username,
             'creator_username': creator.username,
             'description': description}]

        # validation
        if value < 1 or value > creator.account.balance:
            raise P2PIllegalAmount(value)
        if creator.username == receiver_username:
            raise SelfMoneyTransfer()
        if description == '':
            raise EmptyDescriptionError()
        receiver_q = User.objects.filter(username=receiver_username)
        if receiver_q.count() != 1:
            raise UserDoesNotExist(receiver_username)
        receiver = User.objects.get(username=receiver_username)

        new_transaction = Transaction.new_transaction(creator,
                                                      TransactionType.objects.get(
                                                          name=TransactionTypeEnum.p2p.value),
                                                      formset_data)



        Money.new_money(receiver, value,
                        MoneyType.objects.get(name=MoneyTypeEnum.p2p.value),
                        description,
                        new_transaction)
        return new_transaction

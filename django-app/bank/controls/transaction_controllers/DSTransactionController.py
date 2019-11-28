

from django.contrib.auth.models import User
from django.forms import formset_factory

from bank.constants import TransactionTypeEnum, AttendanceTypeEnum, AttendanceBlockEnum, WORKOUT_BUDGET, MoneyTypeEnum, \
    DS_REWARD
from bank.controls.transaction_controllers.TableTransactionController import TableTransactionController
from bank.forms import FacAttendForm, WorkoutForm, DSKernelForm
from bank.models.Money import Money
from bank.models.TransactionType import TransactionType
from bank.models.MoneyType import MoneyType
from bank.models.Transaction import Transaction

class DSTransactionController(TableTransactionController):
    template_url = 'bank/add/add_ds.html'

    value_show_name = 'Дежурил'
    header = "Дежурство по столовой"


    @staticmethod
    def _get_kernel_form():
        return DSKernelForm


    @staticmethod
    def get_initial_form_data(creator_username):
        initial = super(DSTransactionController, DSTransactionController).get_initial_form_data(
            creator_username)
        for in_data in initial:
            in_data['money_type'] = MoneyTypeEnum.potato.value
        return initial

    @staticmethod
    def get_transaction_from_form_data(formset_data, update_of):
        first_form = formset_data[0]
        creator = User.objects.get(username=first_form['creator_username'])
        new_transaction = Transaction.new_transaction(creator, TransactionType.objects.get(
            name=TransactionTypeEnum.ds.value),
                                                      formset_data, update_of)
        attendees_count = sum([a['attended'] for a in formset_data])
        if attendees_count:
            money_type = MoneyType.objects.get(name=first_form['money_type'])
            reward = DSTransactionController._get_reward(attendees_count, money_type)

            for atomic_data in formset_data:
                attended = atomic_data['attended']
                if attended:
                    receiver = User.objects.get(username=atomic_data['receiver_username'])
                    Money.new_money(receiver, reward, money_type,
                                          first_form['description'],
                                          new_transaction)

        return new_transaction

    @staticmethod
    def _get_reward(attendees_count, money_type):
        return DS_REWARD.get(money_type.name)/attendees_count

from django.contrib.auth.models import User
from django.forms import formset_factory

from bank.constants import UserGroups, MoneyTypeEnum
from bank.controls.transaction_controllers.TableTransactionController import TableTransactionController
from bank.forms import GeneralMoneyKernelForm
from bank.models import Transaction, Money, MoneyType


class GeneralTransactionController(TableTransactionController):
    template_url = 'bank/add/add_general_money.html'

    @staticmethod
    def get_blank_form():
        students_query = User.objects.filter(groups__name__contains=UserGroups.student.value)

        general_money_formset = formset_factory(GeneralMoneyKernelForm,
                                                max_num=len(students_query))
        return general_money_formset

    @staticmethod
    def get_initial_form_data(creator_username):
        students_query = User.objects.filter(groups__name__contains=UserGroups.student.value).order_by('account__party',
                                                                                                       'last_name')
        initial = [
            {'student_name': user.account.long_name(), 'student_party': user.account.party,
             'receiver_username': user.username, 'creator_username': creator_username, 'description': 'stub value',
             'transaction_type': MoneyTypeEnum.staff_help.value} for user in students_query]
        initial[0]['description'] = ''
        return initial

    @staticmethod
    def get_transaction_from_form_data(formset_data, update_of):

        first_form = formset_data[0]
        creator = User.objects.get(username=first_form['creator_username'])

        new_transaction = Transaction.new_transaction(creator, MoneyType.objects.get(name=first_form['transaction_type']).related_transaction_type,
                                                      formset_data, update_of)
        for atomic_data in formset_data:
            value = atomic_data['value']
            if value:
                receiver = User.objects.get(username=atomic_data['receiver_username'])
                Money.new_money(receiver, atomic_data['value'], MoneyType.objects.get(name=first_form['transaction_type']),
                                first_form['description'],
                                new_transaction)
        return new_transaction
from django.contrib.auth.models import User
from django.forms import formset_factory

from bank.constants import UserGroups, NUM_OF_PARTIES, MoneyTypeEnum
from bank.controls.transaction_controllers.TransactionController import TransactionController
from bank.forms import GeneralMoneyKernelForm, GeneralMoneyFormSet
from bank.models import Transaction, Money


class GeneralTransactionController(TransactionController):
    template_url = 'bank/add_trans/trans_add_general_money.html'

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
    def get_render_map_update():
        students_query = User.objects.filter(groups__name__contains=UserGroups.student.value)
        endtable = []
        starttable = []
        marker = 0
        for party in range(1, NUM_OF_PARTIES + 1):
            starttable.append(marker + 1)
            marker += len(students_query.filter(account__party=party))
            endtable.append(marker)

        return {'markup': {'endtable': endtable, 'starttable': starttable}}

    @staticmethod
    def get_transaction_from_form_data(formset_data):

        first_form = formset_data[0]
        receiver = User.objects.get(username=first_form['receiver_username'])
        creator = User.objects.get(username=first_form['creator_username'])

        new_transaction = Transaction.new_transaction(creator, first_form['transaction_type'].related_transaction_type, formset_data)
        for atomic_data in formset_data:
            value = atomic_data['value']
            if value:
                Money.new_money(receiver, atomic_data['value'], first_form['transaction_type'], first_form['description'],
                                new_transaction)
        return new_transaction

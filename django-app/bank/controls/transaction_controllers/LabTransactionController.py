from bank.forms import LabKernelForm

from django.contrib.auth.models import User
from django.forms import formset_factory

from bank.constants import MoneyTypeEnum, TransactionTypeEnum, AttendanceTypeEnum
from bank.controls.transaction_controllers.TransactionController import TransactionController
from bank.models.Money import Money
from bank.models.TransactionType import TransactionType
from bank.models.Attendance import Attendance
from bank.models.AttendanceType import AttendanceType
from bank.models.MoneyType import MoneyType
from bank.models.Transaction import Transaction

class LabTransactionController(TransactionController):
    template_url = 'bank/add/add_lab.html'

    @classmethod
    def get_blank_form(cls, creator_username):
        lab_formset = formset_factory(LabKernelForm, max_num=1)
        return lab_formset

    @staticmethod
    def get_initial_form_data(creator_username):
        return [{'receiver_username_1': None,'receiver_username_2': None, 'creator_username': creator_username, 'description': ''}]

    @staticmethod
    def get_transaction_from_form_data(formset_data, update_of):

        first_form = formset_data[0]
        creator = User.objects.get(username=first_form['creator_username'])

        new_transaction = Transaction.new_transaction(creator, TransactionType.objects.get(name=TransactionTypeEnum.lab.value),
                                                      formset_data, update_of)

        money_type = MoneyType.objects.get(name=MoneyTypeEnum.lab_pass.value)
        att_type = AttendanceType.objects.get(name=AttendanceTypeEnum.lab_pass.value)
        receiver_1 = User.objects.get(username=first_form['receiver_username_1'])
        receiver_2 = User.objects.get(username=first_form['receiver_username_2'])

        description = first_form['description']
        description_1 = "{} \nПартнер: {}".format(description, receiver_2.account.long_name())
        description_2 = "{} \nПартнер: {}".format(description, receiver_1.account.long_name())


        Money.new_money(receiver_1, first_form['value_1'],
                        money_type,
                        description_1,
                        new_transaction)

        Money.new_money(receiver_2, first_form['value_2'],
                        money_type,
                        description_2,
                        new_transaction)

        Attendance.new_attendance(receiver_1, 1,
                                  att_type,
                                  description_1, first_form['date'],
                                  new_transaction)

        Attendance.new_attendance(receiver_2, 1,
                        att_type,
                        description_2, first_form['date'],
                        new_transaction)
        return new_transaction

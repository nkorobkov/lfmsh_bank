from django.contrib.auth.models import User

from bank.constants import TransactionTypeEnum, AttendanceTypeEnum, MoneyTypeEnum
from bank.controls.transaction_controllers.TableTransactionController import TableTransactionController
from bank.forms import FacPassKernelForm
from bank.models.Money import Money
from bank.models.TransactionType import TransactionType
from bank.models.Attendance import Attendance
from bank.models.AttendanceType import AttendanceType
from bank.models.MoneyType import MoneyType
from bank.models.Transaction import Transaction

class FacPassTransactionController(TableTransactionController):
    template_url = 'bank/add/add_fac_pass.html'
    value_show_name = 'Баксы за зачет'
    header = "Зачет по факультативу"

    @staticmethod
    def _get_kernel_form():
        return FacPassKernelForm


    @staticmethod
    def get_transaction_from_form_data(formset_data, update_of):

        first_form = formset_data[0]
        creator = User.objects.get(username=first_form['creator_username'])

        new_transaction = Transaction.new_transaction(creator, TransactionType.objects.get(
            name=TransactionTypeEnum.fac_pass.value), formset_data, update_of)
        for atomic_data in formset_data:
            value = atomic_data['value']
            if value:
                receiver = User.objects.get(username=atomic_data['receiver_username'])
                Money.new_money(receiver, atomic_data['value'],
                                MoneyType.objects.get(name=MoneyTypeEnum.fac_pass.value),
                                first_form['description'],
                                new_transaction)

                Attendance.new_attendance(receiver, 1,
                                          AttendanceType.objects.get(name=AttendanceTypeEnum.fac_pass.value),
                                          first_form['description'], first_form['date'],
                                          new_transaction)

        return new_transaction

from django.contrib.auth.models import User

from bank.constants import TransactionTypeEnum, AttendanceTypeEnum, AttendanceBlockEnum
from bank.controls.transaction_controllers.TableTransactionController import TableTransactionController
from bank.forms import FacAttendForm
from bank.models.TransactionType import TransactionType
from bank.models.Attendance import Attendance
from bank.models.AttendanceType import AttendanceType
from bank.models.Transaction import Transaction

class FacAttendTransactionController(TableTransactionController):
    template_url = 'bank/add/add_fac_attend.html'
    value_show_name = 'Посетил'
    header = "Занятие факультатива"

    @staticmethod
    def _get_kernel_form():
        return FacAttendForm

    @staticmethod
    def get_initial_form_data(creator_username):
        initial = super(FacAttendTransactionController,FacAttendTransactionController).get_initial_form_data(creator_username)
        for in_data in initial:
            in_data['block'] = AttendanceBlockEnum.fac_1.value
        initial[0]['block'] = None
        return initial

    @staticmethod
    def get_transaction_from_form_data(formset_data, update_of):
        first_form = formset_data[0]
        creator = User.objects.get(username=first_form['creator_username'])
        new_transaction = Transaction.new_transaction(creator, TransactionType.objects.get(
            name=TransactionTypeEnum.fac_attend.value),
                                                      formset_data, update_of)
        for atomic_data in formset_data:
            attended = atomic_data['attended']
            if attended:
                receiver = User.objects.get(username=atomic_data['receiver_username'])
                Attendance.new_attendance(receiver, 1,
                                AttendanceType.objects.get(name=AttendanceTypeEnum.fac_attend.value),
                                first_form['description'], first_form['date'],
                                new_transaction, first_form['block'])
        return new_transaction

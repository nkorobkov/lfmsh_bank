from django.contrib.auth.models import User

from bank.constants import TransactionTypeEnum, AttendanceTypeEnum, AttendanceBlockEnum, WORKOUT_BUDGET, MoneyTypeEnum
from bank.controls.transaction_controllers.TableTransactionController import TableTransactionController
from bank.forms import WorkoutForm
from bank.models.TransactionType import TransactionType
from bank.models.Money import Money
from bank.models.Attendance import Attendance
from bank.models.AttendanceType import AttendanceType
from bank.models.MoneyType import MoneyType
from bank.models.Transaction import Transaction

class WorkoutTransactionController(TableTransactionController):
    template_url = 'bank/add/add_workout.html'

    value_show_name = 'Посетил'
    header = "Зарядка"


    @staticmethod
    def _get_kernel_form():
        return WorkoutForm


    @staticmethod
    def get_transaction_from_form_data(formset_data, update_of):
        first_form = formset_data[0]
        creator = User.objects.get(username=first_form['creator_username'])
        new_transaction = Transaction.new_transaction(creator, TransactionType.objects.get(
            name=TransactionTypeEnum.workout.value),
                                                      formset_data, update_of)
        attendance_block_name = AttendanceBlockEnum.workout.value
        attendees_count = sum([a['attended'] for a in formset_data])
        reward = WorkoutTransactionController._get_reward(attendees_count)

        for atomic_data in formset_data:
            attended = atomic_data['attended']
            if attended:
                receiver = User.objects.get(username=atomic_data['receiver_username'])
                Attendance.new_attendance(receiver, 1,
                                AttendanceType.objects.get(name=AttendanceTypeEnum.workout.value),
                                first_form['description'], first_form['date'],
                                new_transaction, attendance_block_name)

                Money.new_money(receiver, reward,
                                      MoneyType.objects.get(name=MoneyTypeEnum.workout.value),
                                      first_form['description'],
                                      new_transaction)

        return new_transaction

    @staticmethod
    def _get_reward(attendees_count):
        if attendees_count:
            return max(1, WORKOUT_BUDGET/attendees_count)
        return 0

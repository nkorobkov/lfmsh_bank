from django.contrib.auth.models import User
from django.forms import formset_factory

from bank.constants import TransactionTypeEnum, AttendanceTypeEnum, AttendanceBlockEnum, MoneyTypeEnum, LECTURE_PENALTY
from bank.controls.transaction_controllers.TableTransactionController import TableTransactionController
from bank.forms import LectureForm
from bank.models import Transaction, TransactionType, Attendance, AttendanceType, Money, MoneyType


class LectureTransactionController(TableTransactionController):
    template_url = 'bank/add/add_lecture.html'
    value_show_name = 'Посетил'
    header = "Лекция"

    @staticmethod
    def _get_kernel_form():
        return LectureForm


    @staticmethod
    def get_transaction_from_form_data(formset_data, update_of):
        first_form = formset_data[0]
        creator = User.objects.get(username=first_form['creator_username'])
        new_transaction = Transaction.new_transaction(creator, TransactionType.objects.get(
            name=TransactionTypeEnum.lecture.value),
                                                      formset_data, update_of)

        attendance_block_name = AttendanceBlockEnum.lecture.value
        money_type = MoneyType.objects.get(name=MoneyTypeEnum.fine_lecture.value)

        for atomic_data in formset_data:
            attended = atomic_data['attended']
            receiver = User.objects.get(username=atomic_data['receiver_username'])
            if attended:
                attendance_type_name = AttendanceTypeEnum.lecture_attend.value
            else:
                attendance_type_name = AttendanceTypeEnum.lecture_miss.value
                fine_value = LectureTransactionController._get_lecture_fine(
                    receiver.account.get_counter(AttendanceTypeEnum.lecture_miss.value))
                Money.new_money(receiver, fine_value, money_type,
                                first_form['description'], new_transaction)

            Attendance.new_attendance(receiver, 1,
                                      AttendanceType.objects.get(name=attendance_type_name),
                                      first_form['description'], first_form['date'],
                                      new_transaction, attendance_block_name=attendance_block_name)

        return new_transaction

    @staticmethod
    def _get_lecture_fine(num_missed):
        return -(num_missed + 1) * LECTURE_PENALTY

from django.contrib.auth.models import User
from django.forms import formset_factory

from bank.constants import UserGroups, MoneyTypeEnum, TransactionTypeEnum, AttendanceTypeEnum
from bank.controls.transaction_controllers.TableTransactionController import TableTransactionController
from bank.forms import SeminarKernelForm, SeminarFormset
from bank.models.Money import Money
from bank.models.TransactionType import TransactionType
from bank.models.Attendance import Attendance
from bank.models.AttendanceType import AttendanceType
from bank.models.MoneyType import MoneyType
from bank.models.Transaction import Transaction


class SeminarTransactionController(TableTransactionController):
    template_url = 'bank/add/add_seminar.html'
    value_show_name = 'Посетил'
    header = "Семинар"

    @staticmethod
    def _get_kernel_form():
        return SeminarKernelForm

    @staticmethod
    def get_initial_form_data(creator_username):
        students_query = User.objects.filter(groups__name__contains=UserGroups.student.value).order_by('account__party',
                                                                                                       'last_name')
        initial = [
            {'student_name': user.account.long_name(),
             'student_party': user.account.party,
             'receiver_username': user.username,
             'creator_username': creator_username,
             'description': 'stub value',
             'receiver': user.username,
             'block': 'seminar_1',
             'content_quality': 0,
             'knowledge_quality': 0,
             'presentation_quality': 0,
             'presentation_quality_2': 0,
             'presentation_quality_3': 0,
             'unusual_things': 0,
             'materials': 0,
             'discussion': 0,
             'general_quality': 0

             } for user in students_query]

        initial[0]['description'] = ''
        initial[0]['receiver'] = None
        initial[0]['block'] = None

        for key in SeminarTransactionController._get_mark_keys():
            initial[0][key] = None
        return initial

    @staticmethod
    def get_transaction_from_form_data(formset_data, update_of):
        first_form = formset_data[0]

        mark = sum([int(first_form[key]) for key in SeminarTransactionController._get_mark_keys()])
        money_reward = SeminarTransactionController._get_reward_from_mark(mark)

        creator = User.objects.get(username=first_form['creator_username'])

        new_transaction = Transaction.new_transaction(creator, TransactionType.objects.get(
            name=TransactionTypeEnum.seminar.value),
                                                      formset_data, update_of)

        reader = User.objects.get(username=first_form['receiver'])
        Attendance.new_attendance(reader, 1,
                                  AttendanceType.objects.get(name=AttendanceTypeEnum.seminar_pass.value),
                                  first_form['description'], first_form['date'],
                                  new_transaction, first_form['block'])

        Money.new_money(reader, money_reward,
                        MoneyType.objects.get(name=MoneyTypeEnum.seminar_pass.value),
                        first_form['description'],
                        new_transaction)



        for atomic_data in formset_data:
            attended = atomic_data['attended']
            if attended:
                receiver = User.objects.get(username=atomic_data['receiver_username'])
                Attendance.new_attendance(receiver, 1,
                                          AttendanceType.objects.get(name=AttendanceTypeEnum.seminar_attend.value),
                                          first_form['description'], first_form['date'],
                                          new_transaction, first_form['block'])
        return new_transaction

    @staticmethod
    def _get_mark_keys():
        return ['content_quality',
                'knowledge_quality',
                'presentation_quality',
                'presentation_quality_2',
                'presentation_quality_3',
                'unusual_things',
                'materials',
                'discussion',
                'general_quality']

    @staticmethod
    def _get_reward_from_mark(mark):
        if mark > 0:
            return mark * 5
        else:
            return mark * 10

    @classmethod
    def get_blank_form(cls, creator_username):
        students_query = __class__._get_student_query()
        formset = formset_factory(cls._get_kernel_form(), max_num=len(students_query), formset=SeminarFormset)
        return formset

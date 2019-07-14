from django.contrib.auth.models import User
from django.forms import formset_factory

from bank.constants import UserGroups
from bank.controls.transaction_controllers.TransactionController import TransactionController
from bank.helper_functions import get_students_markup


class TableTransactionController(TransactionController):
    value_show_name = "Посетил"
    header = "Транзакция"

    @classmethod
    def get_render_map_update(cls):
        result = super(TableTransactionController, TableTransactionController).get_render_map_update()
        students_query = User.objects.filter(groups__name__contains=UserGroups.student.value)
        result.update(get_students_markup(students_query))
        if cls.value_show_name:
            result.update({'value_show_name': cls.value_show_name})
        if cls.header:
            result.update({'header': cls.header})

        return result

    @staticmethod
    def get_initial_form_data(creator_username):
        students_query = TableTransactionController._get_student_query()
        initial = [
            {'student_name': user.account.long_name(),
             'student_party': user.account.party,
             'receiver_username': user.username,
             'creator_username': creator_username,
             'description': 'stub value',
             } for user in students_query]
        initial[0]['description'] = ''
        return initial

    @staticmethod
    def _get_student_query():
        return User.objects.filter(groups__name__contains=UserGroups.student.value).order_by('account__party',
                                                                                             'last_name', 'first_name')
    @classmethod
    def get_blank_form(cls, creator_username):
        students_query = __class__._get_student_query()
        return formset_factory(cls._get_kernel_form(), max_num=len(students_query))

    @staticmethod
    def _get_kernel_form():
        raise NotImplementedError("get kernel form not implemented")

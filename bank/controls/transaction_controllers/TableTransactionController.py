from django.contrib.auth.models import User

from bank.constants import UserGroups
from bank.controls.transaction_controllers.TransactionController import TransactionController
from bank.helper_functions import get_students_markup


class TableTransactionController(TransactionController):

    @staticmethod
    def get_render_map_update():
        result = super(TableTransactionController,TableTransactionController).get_render_map_update()
        students_query = User.objects.filter(groups__name__contains=UserGroups.student.value)
        result.update(get_students_markup(students_query))
        return result

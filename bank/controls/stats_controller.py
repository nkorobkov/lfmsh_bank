from bank.constants import UserGroups
from bank.models import Money, Account


def get_student_stats():
    return {'sum_money': sum([a.balance for a in Account.objects.filter(user__groups__name__contains=UserGroups.student.value)])}
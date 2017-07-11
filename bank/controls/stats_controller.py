from bank.constants import UserGroups, Actions, States
from bank.helper_functions import get_perm_name
from bank.models import Money, Account, Transaction


def get_student_stats(user):
    stats = {}

    if user.has_perm(get_perm_name(Actions.see.value, UserGroups.student.value, "balance")):
        stats.update({'sum_money': sum(
            [a.balance for a in Account.objects.filter(user__groups__name__contains=UserGroups.student.value)])})

    if user.has_perm(get_perm_name(Actions.process.value, UserGroups.student.value, "created_transactions")):
        stats.update({'created_students_len': Transaction.objects.filter(
            creator__groups__name__in=[UserGroups.student.value]).filter(state__name=States.created.value).__len__()})

    if user.has_perm(get_perm_name(Actions.process.value, UserGroups.staff.value, "created_transactions")):
        stats.update({'created_staff_len': Transaction.objects.filter(
            creator__groups__name__in=[UserGroups.staff.value]).filter(state__name=States.created.value).__len__()})

    return stats

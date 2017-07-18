from bank.constants import UserGroups, Actions, States
from bank.helper_functions import get_perm_name
from bank.models import Money, Account, Transaction
import statistics


def get_student_stats(user):
    stats = {}

    if user.has_perm(get_perm_name(Actions.see.value, UserGroups.student.value, "balance")):
        student_accounts = Account.objects.filter(user__groups__name__contains=UserGroups.student.value)
        balances = [a.balance for a in student_accounts]
        stats.update({
            'sum_money': int(sum(balances)),
            'mean_money': int(statistics.mean(balances))  
        })
        
        print(stats)

    if user.has_perm(get_perm_name(Actions.process.value, UserGroups.student.value, "created_transactions")):
        stats.update({'created_students_len': Transaction.objects.filter(
            creator__groups__name__in=[UserGroups.student.value]).filter(state__name=States.created.value).__len__()})

    if user.has_perm(get_perm_name(Actions.process.value, UserGroups.staff.value, "created_transactions")):
        stats.update({'created_staff_len': Transaction.objects.filter(
            creator__groups__name__in=[UserGroups.staff.value]).filter(state__name=States.created.value).__len__()})

    return stats

def get_report_student_stats(user):
    stats = {}

    if user.has_perm(get_perm_name(Actions.see.value, UserGroups.student.value, "balance")):
        student_accounts = Account.objects.filter(user__groups__name__contains=UserGroups.student.value)
        balances = [a.balance for a in student_accounts]
        stats.update({
            'sum_money': int(sum(balances)),
            'mean_money': int(statistics.mean(balances))  
        })
        
        accounts_info = []
        for acc in student_accounts:
            money = acc.get_all_money()
            acc_info = {
                'name': acc.long_name(),
                'balance_stored': acc.balance,
                'party': acc.party,
                'balance_calculated': get_balance_change_from_money_list(money, acc.user.username),
                'earned_work': get_balance_change_from_money_list(filter(lambda m: m.type.group_general == 'work' , money), acc.user.username),
                'earned_fine': get_balance_change_from_money_list(filter(lambda m: m.type.group_general == 'fine', money), acc.user.username),
                'earned_activity': get_balance_change_from_money_list(filter(lambda m: m.type.group_general == 'activity', money), acc.user.username),
                'earned_sport': get_balance_change_from_money_list(filter(lambda m: m.type.group_general == 'sport', money), acc.user.username),
                'earned_studies': get_balance_change_from_money_list(filter(lambda m: m.type.group_general == 'studies', money), acc.user.username),
            }
            accounts_info.append(acc_info)
        stats.update({"accounts_info": accounts_info})
    return stats
    

def get_balance_change_from_money_list(money_list, username):
    r = 0
    for t in money_list:
        if t.counted:
            if t.receiver.username == username:
                r = r + t.value
            else:
                r = r - t.value
    
    return r
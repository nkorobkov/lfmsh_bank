import math

import logging

from bank.constants import UserGroups, Actions, States, AttendanceTypeEnum, OBL_STUDY_NEEDED, BALANCE_DANGER, \
    BALANCE_WARNING
from bank.helper_functions import get_perm_name

from bank.models.Attendance import Attendance
from bank.models.AttendanceType import AttendanceType
from bank.models.Transaction import Transaction
from bank.models.Account import Account


import statistics

log = logging.getLogger("unexpected_things_logger")


def get_student_stats(user):
    stats = {}

    if user.has_perm(get_perm_name(Actions.see.value, UserGroups.student.value, "balance")):
        student_accounts = Account.objects.filter(user__groups__name__contains=UserGroups.student.value)
        balances = [a.balance for a in student_accounts]
        stats.update({
            'sum_money': int(sum(balances)),
            'mean_money': int(statistics.mean(balances))
        })

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
        student_accounts = Account.objects.filter(user__groups__name__contains=UserGroups.student.value).order_by(
            'party',
            'user__last_name')
        balances = [a.balance for a in student_accounts]
        stats.update({
            'sum_money': int(sum(balances)),
            'mean_money': int(statistics.mean(balances)),
            'st_dev': round(statistics.stdev(balances), 2),
        })
        accounts_info = []
        for acc in student_accounts:
            money = acc.get_all_money()
            acc_info = {
                'acc': acc,
                'name': acc.long_name(),
                'str_balance': acc.get_balance(),
                'balance_stored': acc.balance,
                'party': acc.party,
                'balance_calculated': get_balance_change_from_money_list(money, acc.user.username),
                'earned_all': get_balance_change_from_money_list(
                    filter(lambda m: m.type.group_general not in ['fine', 'purchase', 'technicals', 'p2p'], money),
                    acc.user.username),
                'earned_work': get_balance_change_from_money_list(
                    filter(lambda m: m.type.group_general == 'work', money), acc.user.username),
                'earned_fine': get_balance_change_from_money_list(
                    filter(lambda m: m.type.group_general == 'fine', money), acc.user.username),
                'earned_activity': get_balance_change_from_money_list(
                    filter(lambda m: m.type.group_general == 'activity', money), acc.user.username),
                'earned_sport': get_balance_change_from_money_list(
                    filter(lambda m: m.type.group_general == 'sport', money), acc.user.username),
                'earned_studies': get_balance_change_from_money_list(
                    filter(lambda m: m.type.group_general == 'studies', money), acc.user.username),
                'counters': get_counters_of_user_who_is(user, acc.user, UserGroups.student.value)
            }
            accounts_info.append(acc_info)
            if math.fabs(acc_info['balance_calculated'] - acc_info['balance_stored']) > 10:
                log.warning("balances for {} differs more than {}".format(acc, 10))

        best_activity = max(get_list_from_dict_list_by_key(accounts_info, 'earned_activity'))
        best_work = max(get_list_from_dict_list_by_key(accounts_info, 'earned_work'))
        best_sport = max(get_list_from_dict_list_by_key(accounts_info, 'earned_sport'))
        best_studies = max(get_list_from_dict_list_by_key(accounts_info, 'earned_studies'))
        best_all = max(get_list_from_dict_list_by_key(accounts_info, 'earned_all'))
        best_balance = max(get_list_from_dict_list_by_key(accounts_info, 'balance_stored'))

        for acc_info in accounts_info:
            acc_info['is_best_activity'] = acc_info['earned_activity'] == best_activity
            acc_info['is_best_work'] = acc_info['earned_work'] == best_work
            acc_info['is_best_sport'] = acc_info['earned_sport'] == best_sport
            acc_info['is_best_studies'] = acc_info['earned_studies'] == best_studies
            acc_info['is_best_all'] = acc_info['earned_all'] == best_all
            if BALANCE_DANGER < acc_info['balance_stored'] < BALANCE_WARNING:
                acc_info['row_class'] = 'warning'
            elif acc_info['balance_stored'] <= BALANCE_DANGER:
                acc_info['row_class'] = 'danger'
            elif acc_info['balance_stored'] == best_balance:
                acc_info['row_class'] = 'my-success'
            else:
                acc_info['row_class'] = ''

        stats.update({"accounts_info": accounts_info})
        counters_list = get_list_from_dict_list_by_key(accounts_info, 'counters')
        stats.update({"sum_lab": sum([t['val'][AttendanceTypeEnum.lab_pass.value] for t in counters_list]),
                      "sum_fac": sum([t['val'][AttendanceTypeEnum.fac_attend.value] for t in counters_list]),
                      "sum_sem_pass": sum([t['val'][AttendanceTypeEnum.seminar_pass.value] for t in counters_list]),
                      "sum_sem_attend": sum([t['val'][AttendanceTypeEnum.seminar_attend.value] for t in counters_list])})

    return stats


def get_list_from_dict_list_by_key(dict_list, keyy):
    return [dict[keyy] for dict in dict_list]


def get_balance_change_from_money_list(money_list, username):
    r = 0
    for t in money_list:
        if t.counted:
            if t.receiver.username == username:
                r = r + t.value
            else:
                r = r - t.value

    return r


def get_counters_of_user_who_is(user, target_user, group):
    if not user.has_perm(get_perm_name(Actions.see.value, group, "attendance")):
        return None

    all_counters = Attendance.objects.filter(receiver=target_user).filter(counted=True)
    info = {"study_needed": OBL_STUDY_NEEDED, "fac_pass_needed": target_user.account.fac_needed(),
            "lab_pass_needed": target_user.account.lab_needed()}
    counters_val = {}
    for counter_type in AttendanceType.objects.all():
        counter_sum = sum([c.value for c in all_counters.filter(type=counter_type)])
        counters_val.update({counter_type.name: int(counter_sum)})
    info.update({"study": counters_val.get(AttendanceTypeEnum.fac_attend.value) + counters_val.get(
        AttendanceTypeEnum.seminar_attend.value)})
    info.update(
        {"next_missed_lec_fine": target_user.account.get_next_missed_lec_penalty(),
         "expected_fine": target_user.account.get_final_study_fine()})
    return {"val": counters_val, "info": info}

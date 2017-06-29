# coding=utf-8
from .constants import *

zaryadka_budget = 40.
p2p_buf = 40.
p2p_proc = 0.7
daily_tax = -20
sem_needed = 18
activity_money = {1: 20, 2: 15, 3: 10, 4: 5}


def zaryadka(num_of_attendants):
    if num_of_attendants != 0:
        return max(1, ZARYADKA_BUDGET / num_of_attendants)
    return 0


def seminar(score):
    if score > 0:
        return score * 5
    else:
        return score * 10


def get_students_markup(students):
    endtable = []
    starttable = []
    marker = 0
    for party in range(1, NUM_OF_PARTIES + 1):
        starttable.append(marker + 1)
        marker += len(students.filter(account__party=party))
        endtable.append(marker)

    return {'markup': {'endtable': endtable, 'starttable': starttable}}
'''

def lec(score, sum_score, budget, num_of_attendants):
    print(num_of_attendants, sum_score)
    print(score, end=' ')
    sc = max(0, (float(score))) ** (0.5)

    print(sc, end=' ')
    value = max(0., (float(budget) * num_of_attendants) * sc / (float(sum_score)))
    print(value)
    return value
'''

def lec_pen(missed):
    return (missed + 1) * 10


def get_tax_desc():
    return str('Поздравляем 👑Глеба Бурдонова👑 с получением Золотого Аккаунта Банка ЛФМШ!', 'utf-8')


def sem_fac_penalty(n):
    step = SEM_STEP
    s = INITIAL_STEP_SEM
    a = 0
    for i in range(n):
        a += s
        s += step

    return a


def get_student_stats():
    return {'sum_money': 1000}


def get_perm_name(*args):
    args = map(str, args)
    return 'bank.' + '_'.join(args)

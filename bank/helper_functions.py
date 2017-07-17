# coding=utf-8
from .constants import *

zaryadka_budget = 40.
p2p_buf = 40.
p2p_proc = 0.7
daily_tax = -20
sem_needed = 18
activity_money = {1: 20, 2: 15, 3: 10, 4: 5}


def get_students_markup(students):
    endtable = []
    starttable = []
    marker = 0
    for party in range(1, NUM_OF_PARTIES + 1):
        starttable.append(marker + 1)
        marker += len(students.filter(account__party=party))
        endtable.append(marker)

    return {'markup': {'endtable': endtable, 'starttable': starttable}}


def sem_fac_penalty(n):
    step = SEM_STEP
    s = INITIAL_STEP_SEM
    a = 0
    for i in range(n):
        a += s
        s += step

    return a


def get_next_missed_lec_penalty(missed):
    return (missed + 1) * LECTURE_PENALTY


def get_perm_name(*args):
    args = map(str, args)
    return 'bank.' + '_'.join(args)

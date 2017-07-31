# coding=utf-8
from .constants import *


def get_students_markup(students):
    endtable = []
    starttable = []
    marker = 0
    for party in range(1, NUM_OF_PARTIES + 1):
        starttable.append(marker + 1)
        marker += len(students.filter(account__party=party))
        endtable.append(marker)

    return {'markup': {'endtable': endtable, 'starttable': starttable}}


def get_perm_name(*args):
    args = map(str, args)
    return 'bank.' + '_'.join(args)

# coding=utf-8
from .constants import *

import string
import secrets


def get_students_markup(students):
  endtable = []
  starttable = []
  marker = 0
  for party in range(1, NUM_OF_PARTIES + 1):
    starttable.append(marker + 1)
    marker += len(students.filter(account__party=party))
    endtable.append(marker)

  return {
      'markup': {
          'endtable': endtable,
          'starttable': starttable,
          'rowbreak': endtable[1]
      }
  }


def get_session_day():
  day = (datetime.date.today() - FIRST_DAY_DATE).days + 1
  return day


def get_tax_from_session_day(day):
  return TAX_FROM_DAY[day]


def get_perm_name(*args):
  args = map(str, args)
  return 'bank.' + '_'.join(args)


def generate_password(n):
  alphanumeric = string.printable[:62]
  without_hard_to_read_chars = alphanumeric.translate(
      {ord(c): None for c in 'l1Iio0O'})
  return ''.join(secrets.choice(without_hard_to_read_chars) for i in range(n))

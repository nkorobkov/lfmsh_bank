# coding=utf-8
from bank.constants.UserGroups import UserGroups
import datetime

__author__ = 'Insolia'

SIGN = '@'
BANKIR_USERNAME = 'bank_manager'

PERMISSION_RESPONSIBLE_GROUPS = [UserGroups.staff.value, UserGroups.student.value, UserGroups.admin.value]

FIRST_DAY_DATE = datetime.datetime(2018, 8, 6, 0, 0).date()

BOOK_CERTIFICATE_VALUE = 50
INITIAL_MONEY = 120
INITIAL_MONEY_DESC = 'Поздравляем с началом экономической игры!'

WORKOUT_BUDGET = 25.
EXAM_BUDGET = 80.
ACTIVITY_REWARD = {'sport_activity': {'single': [20., 15., 10., 5.]},
                   'evening_activity': {'single': [20., 15., 10.], 'team': [120., 100., 80.]},
                   'day_activity': {'single': [20., 15., 10.], 'team': [120., 100., 80.]}}
DS_REWARD = {
    'potato': 60., "bread_cut": 60., "serving": 60.
}

OBL_STUDY_NEEDED = 18
LAB_PASS_NEEDED = {7: 3, 8: 3, 9: 2, 10: 2, 11: 2}
FAC_PASS_NEEDED = {7: 0, 8: 0, 9: 1, 10: 1, 11: 1}

LAB_PENALTY = 50  # for each unmade lab
LECTURE_PENALTY_INITIAL = 10
LECTURE_PENALTY_STEP = 20  # for each missed on new miss
FAC_PENALTY = 100  # for each not attended fac
SEM_NOT_READ_PEN = 100


INITIAL_STEP_OBL_STD = 15 # for first
STEP_OBL_STD = 5  # cumulative constant for each next


NUM_OF_PARTIES = 4

BALANCE_DANGER = 0
BALANCE_WARNING = 30

USE_PICS = False
DEFAULT_PIC_PATH = 'bank/avatars/default.jpg'


TAX_FROM_DAY = {
    1: 0,
    2: 5,
    3: 7,
    4: 9,
    5: 12,
    6: 15,
    7: 18,
    8: 20,
    9: 22,
    10: 23,
    11: 24,
    12: 25,
    13: 25,
    14: 25,
    15: 25,
    16: 25,
    17: 25,
    18: 25,
    19: 25,
    20: 25,
    21: 25
}

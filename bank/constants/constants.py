# coding=utf-8
from bank.constants.UserGroups import UserGroups

__author__ = 'Insolia'

SIGN = '@'
BANKIR_USERNAME = 'bank_manager'

PERMISSION_RESPONSIBLE_GROUPS = [UserGroups.staff.value, UserGroups.student.value, UserGroups.admin.value]

DAILY_TAX = 20
BOOK_CERTIFICATE_VALUE = 50
INITIAL_MONEY = 180
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

LAB_PENALTY = 20  # for each unmade lab
LECTURE_PENALTY = 10  # for each missed on new miss
FAC_PENALTY = 60  # for each not attended fac
SEM_NOT_READ_PEN = 100


INITIAL_STEP_OBL_STD = 10 # for first
STEP_OBL_STD = 5  # cumulative constant for each next


NUM_OF_PARTIES = 4

BALANCE_DANGER = 0
BALANCE_WARNING = 30

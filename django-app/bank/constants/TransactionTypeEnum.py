from enum import Enum


class TransactionTypeEnum(Enum):
    general_money = 'general_money'
    p2p = 'p2p'
    seminar = 'seminar'
    fac_attend = 'fac_attend'
    lecture = 'lecture'
    workout = 'workout'
    fine = 'fine'
    purchase = 'purchase'
    fac_pass = 'fac_pass'
    exam = 'exam'
    activity = 'activity'
    lab = "lab"
    ds = 'dining_services'
    tax = 'tax'

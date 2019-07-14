from enum import Enum


class MoneyTypeEnum(Enum):
    staff_help = 'staff_help'
    art_help = 'art_help'
    radio_help = 'radio_help'

    p2p='p2p'
    seminar_pass = 'seminar_pass_reward'
    workout = 'workout_reward'
    fine_lecture = 'fine_lecture'
    fine_any = 'fine_any'
    exam = 'exam'
    fac_pass = 'fac_pass_reward'
    books = 'books'
    evening_activity = 'evening_activity'
    sport_activity = 'sport_activity'
    lab_pass = "lab_pass_reward"
    potato = 'potato'
    tax = 'tax'
    initial = 'initial'

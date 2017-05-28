# coding=utf-8
from constants import *

zaryadka_budget = 40.
p2p_buf = 40.
p2p_proc = 0.7
daily_tax = -20
sem_needed = 18
activity_money = {1: 20, 2: 15, 3: 10, 4: 5}

from models import *
from dal import autocomplete


class PionerAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return 0

        qs = User.objects.all()

        if self.q:
            qs = qs.filter(last_name__istartswith=self.q)

        return qs


def zaryadka(num_of_attendants):
    if num_of_attendants != 0:
        return max(1, ZARYADKA_BUDGET / num_of_attendants)
    return 0


def seminar(score):
    if score > 0:
        return score * 5
    else:
        return score * 10


def lec(score, sum_score, budget, num_of_attendants):
    print num_of_attendants, sum_score
    print score,
    sc = max(0,(float(score)))**(0.5)
    
    print sc, 
    value = max(0,(float(budget)*num_of_attendants) * sc / (float(sum_score)))
    print value
    return value


def lec_pen(missed):
    return (missed + 1) * 10


def get_tax_desc():
    return unicode('Поздравляем 👑Глеба Бурдонова👑 с получением Золотого Аккаунта Банка ЛФМШ!', 'utf-8')


def sem_fac_penalty(n):

    step = SEM_STEP
    s = INITIAL_STEP_SEM
    a = 0
    for i in range(n):
        a +=s
        s +=step


    return a

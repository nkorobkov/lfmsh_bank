__author__ = 'Insolia'

from bank.models import *
import csv
from transliterate import translit
from django.contrib.auth.models import Group
import random
from bank.constants import *
import string


def get_pd(str):

    a = random.sample(string.printable[:62], 8)
    s = ''
    for c in a:
        s = s+c
    return s




### execfile('add_pioners_script.py')

p_f = open('meta_files/pio_table_2.csv')
p_out = open('meta_files/logins_pio.txt', 'w')

g = Group.objects.get(name='pioner')

for p in csv.reader(p_f):
    ln = p[0].decode('utf-8')
    fn = p[1].decode('utf-8')
    tn = p[2].decode('utf-8')

    grad = p[4].decode('utf-8')
    otr =  p[3].decode('utf-8')

    login = translit(fn[0], 'ru', reversed=True) + translit(tn[0], 'ru', reversed=True) + translit(ln, 'ru',
                                                                                                   reversed=True)
    login = login.lower().replace("'","")
    pd = get_pd(login)

    new_u = User.objects.create_user(first_name=fn, last_name=ln, username=login, password=pd)
    new_u.save()
    g.user_set.add(new_u)
    new_a = Account(user=new_u, third_name=tn, grade=grad, otr=otr)
    new_a.save()

    initial = Transaction.create_trans(recipient=new_u, creator=User.objects.get(username='admin'), value=INITIAL_MONEY,
                                       description=INITIAL_MONEY_DESC, type=TransactionType.objects.get(name='initial'),
                                       status=TransactionState.objects.get(name="PR"))
    print((ln + ' ' + fn + '\n' + 'login: ' + login + ' password: ' + pd))
    info = ln + ' ' + fn + '\n' + 'login: ' + login + ' password: ' + pd

    p_out.write(info.encode('utf-8'))
    p_out.write('\n\n')


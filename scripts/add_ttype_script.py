__author__ = 'Insolia'

from bank.models import *
import csv
from django.contrib.auth.models import Group
import random




### execfile('add_ttypes_script.py')

p_f = open('meta_files/t_types.csv')

for p in csv.reader(p_f):
    hng1 = p[0].decode('utf-8')
    g1 = p[1]
    hng2 = p[2].decode('utf-8')
    g2 = p[3]
    hn = p[4].decode('utf-8')
    n = p[5]

    new_u = TransactionType(human_name=hn, name=n, group1=g1, group2=g2, group1_hn=hng1, group2_hn=hng2)
    new_u.save()

    print new_u
# coding=utf-8
__author__ = 'Insolia'

from bank.models import *
import csv
from transliterate import translit
from django.contrib.auth.models import Group
import random
from bank.constants import *
import string


def get_pd(leng):

    a = random.sample(string.printable[:62], leng)
    s = ''
    for c in a:
        s = s+c
    return s




### execfile('Yanyshev_sucks.py')


p_out = open('meta_files/new_passwords.txt', 'w')
'''
for u in User.objects.filter(groups__name='pioner'):
    
    pd = get_pd(8)
    u.set_password(pd)
    u.save()

    print u.account + 'login: ' + u.username + ' password: ' + pd
    info = u.account +  '\n' + 'login: ' +  u.username + ' password: ' + pd

    p_out.write(info.encode('utf-8'))
    p_out.write('\n ' + '--'*30 +' \n\n')
'''
for u in User.objects.filter(groups__name='pedsostav'):
    
    pd = get_pd(12)
    u.set_password(pd)
    u.save()

    print  'login: ' + u.username + ' password: ' + pd
    info =  '\n' + 'login: ' +  u.username + ' password: ' + pd

    p_out.write(info.encode('utf-8'))
    p_out.write('\n ' + '--'*30 +' \n\n')



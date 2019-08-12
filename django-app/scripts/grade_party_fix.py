# coding=utf-8
__author__ = 'Insolia'

from django.contrib.auth.models import User


#p_out = open('meta_files/new_passwords.txt', 'w')
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
for u in User.objects.filter(groups__name='student'):
    
    a = u.account
    g = a.party
    c = a.grade
    a.party = c
    a.grade = g
    a.save()
    u.save()




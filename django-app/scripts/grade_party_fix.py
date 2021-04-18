# coding=utf-8
__author__ = 'nkorobkov'

from django.contrib.auth.models import User

for u in User.objects.filter(groups__name='student'):

  a = u.account
  g = a.party
  c = a.grade
  a.party = c
  a.grade = g
  a.save()
  u.save()

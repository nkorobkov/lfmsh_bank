# coding=utf-8
import django_tables2 as tables
from .models import *
from django_tables2.utils import A  # alias for Accessor

# -*- coding: utf-8 -*-


class TransTable(tables.Table):
    class Meta:
        model = Transaction
        # add class="paleblue" to <table> tag
        attrs = {'class': 'paleblue table table-striped'}
        exclude = ('last_modified_date','modifier')

    def render_creation_date(self, value):
        return value.strftime("%d.%m.%Y %H:%M")

    def render_creator(self, value):
        return value.account

    def render_recipient(self, value):
        return value.account


class PionerOtrTable(tables.Table):
    class Meta:

        attrs = {'class': 'paleblue table table-striped'}


    name = tables.LinkColumn('bank:trans_list', args=[A('username')], accessor='account.long_name', verbose_name=unicode('Пионер','utf-8'), order_by='last_name')
    balance = tables.Column(accessor='account.get_balance', verbose_name=unicode('Баланс','utf-8'), order_by='account.balance', attrs={'td': {'class': 'text-right text'}})

    def render_balance(self, value):
        return str(value) + '@'


class ZarTable(tables.Table):
    class Meta:
        attrs = {'class': 'paleblue table table-striped'}
    name = tables.Column(accessor='account.long_name', verbose_name=unicode('Пионер','utf-8'), order_by='last_name')

    check = tables.TemplateColumn('<input type="checkbox" name="{{record.username}}" value="0"  {% if record.username  in creation_dict%} checked {% endif %}>',verbose_name=unicode('Посетил','utf-8'))

class LecTable(tables.Table):
    class Meta:
        attrs = {'class': 'paleblue table table-striped'}
    name = tables.Column(accessor='account.long_name', verbose_name=unicode('Пионер','utf-8'), order_by='last_name')

    check = tables.TemplateColumn('<input type="checkbox" name="{{record.username}}" value="0" >',verbose_name=unicode('Посетил','utf-8'))

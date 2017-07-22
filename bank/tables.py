# coding=utf-8
import django_tables2 as tables
from django_tables2 import Column, LinkColumn
from django_tables2.utils import A  # alias for Accessor


# -*- coding: utf-8 -*-


class TransTable(tables.Table):
    class Meta:
        # add class="paleblue" to <table> tag
        attrs = {'class': 'paleblue table table-striped'}

    creator = LinkColumn('bank:user', args=[A('creator.username')],accessor='creator.account.long_name', verbose_name="Cоздатель")
    type = Column(accessor='type.readable_name', verbose_name="Тип")
    state = Column(accessor='state.readable_name', verbose_name="Состояние")
    date_created = Column(accessor='get_creation_timestamp', verbose_name="Дата создания", order_by="creation_timestamp")
    value = Column(accessor='money_count', verbose_name="Сумма", orderable=False)
    receivers = Column(accessor='receivers_count', verbose_name="Получателей", orderable=False)


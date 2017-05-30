# coding=utf-8
from django import forms
from .models import Transaction, Account, TransactionType
from django.forms import ModelChoiceField
import datetime


# -*- coding: utf-8 -*-


class RecipientModelChoiceField(ModelChoiceField):
    def label_from_instance(self, account):
        return str(account.otr) + ' ' + (account.long_name())


class SprecialTransForm(forms.Form):
    '''
    class Meta:
        model = Transaction
        fields = ('recipient', 'value', 'description')
    '''

    recipient = RecipientModelChoiceField(
        queryset=Account.objects.filter(user__groups__name='pioner').order_by('otr', 'user__last_name'),
        label="Получатель")

    type = forms.ModelChoiceField(queryset=TransactionType.objects.all().exclude(name='p2p').exclude(group1='fine'),
                                  label='Тип')

    value = forms.IntegerField(label='Сумма', min_value=0)

    description = forms.CharField(max_length=1000, widget=forms.Textarea, label='Описание')


class LabTransForm(forms.Form):
    recipient = RecipientModelChoiceField(
        queryset=Account.objects.filter(user__groups__name='pioner').order_by('otr', 'user__last_name'),
        label='Получатель')

    description = forms.CharField(max_length=400, widget=forms.Textarea, label='Описание')

    value = forms.IntegerField(label='Сумма', min_value=0)


class SeminarTransForm(forms.Form):
    recipient = RecipientModelChoiceField(queryset=Account.objects.filter(user__groups__name='pioner').order_by('otr',
                                                                                                                'user__last_name'),
                                          label='Расказчик')

    description = forms.CharField(label='Тема и описание', max_length=400, widget=forms.Textarea)

    date = forms.DateField(initial=datetime.date.today)


class FacAttTransForm(forms.Form):
    date = forms.DateField(initial=datetime.date.today)
    description = forms.CharField(label='Название факультатива, возможно описание занятия', max_length=400,
                                  widget=forms.Textarea)


class P2PTransForm(forms.Form):
    '''
    class Meta:
        model = Transaction
        fields = ('recipient', 'value', 'description')
    '''

    def __init__(self, max_value, *args, **kwargs):
        super(P2PTransForm, self).__init__(*args, **kwargs)
        self.fields['value'] = forms.IntegerField(max_value=max_value, label='Сумма', min_value=0)

    recipient = RecipientModelChoiceField(
        queryset=Account.objects.filter(user__groups__name='pioner').order_by('otr', 'user__last_name'),
        label='Получатель')
    description = forms.CharField(max_length=400, widget=forms.Textarea, label='Описание')

    value = forms.IntegerField(label='Сумма', min_value=0)


class FineTransForm(forms.Form):
    recipient = RecipientModelChoiceField(queryset=Account.objects.filter(user__groups__name='pioner').order_by('otr',
                                                                                                                'user__last_name'),
                                          label='Пионер')

    type = forms.ModelChoiceField(queryset=TransactionType.objects.all().filter(group1='fine'),
                                  label='Тип штрафа')
    value = forms.IntegerField(label='Сумма штрафа', max_value=2000, min_value=0,
                               help_text='Ну в 90% случаев штрафуют за мат 10 бачей (c)Ахмеджанов')

    description = forms.CharField(label='Пояснение', max_length=1000, widget=forms.Textarea)

# coding=utf-8
import datetime

from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import ChoiceWidget
from django.shortcuts import get_object_or_404

from bank.constants import UserGroups, P2P_BUFFER, AttendanceTypeEnum
from bank.constants.TransactionTypeEnum import TransactionTypeEnum
from bank.models import MoneyType, AttendanceBlock
from django.forms import BaseFormSet, ModelChoiceField


# -*- coding: utf-8 -*-
class AtomicTypeField(forms.ModelChoiceField):
    def to_python(self, value):
        return value


class MyDateField(forms.DateField):
    def to_python(self, value):
        return str(value)


class MyBlockField(forms.ModelChoiceField):
    def to_python(self, value):
        return value


class ReceiverField(forms.ModelChoiceField):
    def to_python(self, value):
        return value

    def label_from_instance(self, user):
        return '{} {}'.format(user.account.party, user.account.long_name())


class PlaceWidget(ChoiceWidget):
    input_type = 'radio'
    template_name = 'bank/add/widget/place.html'
    option_template_name = ''


class TableKernelForm(forms.Form):
    student_name = forms.CharField(label='Name', max_length=200)
    student_party = forms.IntegerField(label='Party')
    # technical fields not to be used on UI
    receiver_username = forms.CharField(max_length=200)
    creator_username = forms.CharField(max_length=200)


class ValueKernelForm(TableKernelForm):
    value = forms.IntegerField(label='Value', required=False, min_value=1)

    # field that will be used only once from first instance of formset.
    description = forms.CharField(max_length=1000, widget=forms.Textarea({'cols': '40', 'rows': '5'}), label='Описание',
                                  required=True)


class GeneralMoneyKernelForm(ValueKernelForm):
    money_type = AtomicTypeField(label="Тип",
                                 queryset=MoneyType.objects.filter(
                                     related_transaction_type__name=TransactionTypeEnum.general_money.value),
                                 required=True, empty_label=None, to_field_name="name")


class FineKernelForm(ValueKernelForm):
    money_type = AtomicTypeField(label="Тип",
                                 queryset=MoneyType.objects.filter(
                                     related_transaction_type__name=TransactionTypeEnum.fine.value),
                                 required=True, empty_label=None, to_field_name="name")


class PurchaseKernelForm(ValueKernelForm):
    money_type = AtomicTypeField(label="Вид",
                                 queryset=MoneyType.objects.filter(
                                     related_transaction_type__name=TransactionTypeEnum.purchase.value),
                                 required=True, empty_label=None, to_field_name="name")


class ActivityKernelForm(TableKernelForm):
    description = forms.CharField(max_length=1000, widget=forms.Textarea({'cols': '40', 'rows': '5'}), label='Описание',
                                  required=True)

    date = MyDateField(initial=datetime.date.today, label="Дата проведения")
    money_type = AtomicTypeField(label="Вид",
                                 queryset=MoneyType.objects.filter(
                                     related_transaction_type__name=TransactionTypeEnum.activity.value),
                                 required=True, empty_label=None, to_field_name="name")
    cert = forms.BooleanField(required=False)
    place_choices = [(1, "1"), (2, "2"), (3, "3"), (4, "Участник")]
    place = forms.ChoiceField(widget=PlaceWidget, choices=place_choices, required=False)


class ExamKernelForm(ValueKernelForm):
    pass


class FacPassKernelForm(ValueKernelForm):
    date = MyDateField(initial=datetime.date.today, label="Дата проведения")


class AttendKernelForm(TableKernelForm):
    attended = forms.BooleanField(required=False)

    # fields that will be used only once from first instance of formset.
    description = forms.CharField(max_length=1000, widget=forms.Textarea({'cols': '40', 'rows': '5'}), label='Описание',
                                  required=True)

    date = MyDateField(initial=datetime.date.today, label="Дата проведения")


class FacAttendForm(AttendKernelForm):
    block = MyBlockField(label='Блок факультатива',
                         queryset=AttendanceBlock.objects.filter(
                             related_attendance_types__name__in=[AttendanceTypeEnum.fac_attend.value]),
                         required=True, empty_label='Блок', to_field_name='name')


class LectureForm(AttendKernelForm):
    pass


class WorkoutForm(AttendKernelForm):
    pass


class SeminarKernelForm(AttendKernelForm):
    # fields that will be used only once from first instance of formset.
    receiver = ReceiverField(label="Докладчик",
                             queryset=User.objects.filter(
                                 groups__name__in=[UserGroups.student.value]).order_by('account__party',
                                                                                       'last_name'),
                             empty_label="Жертва", to_field_name="username")

    block = MyBlockField(label='Блок семинара',
                         queryset=AttendanceBlock.objects.filter(
                             related_attendance_types__name__in=[AttendanceTypeEnum.seminar_pass.value]),
                         required=True, empty_label='Блок', to_field_name='name')

    # marks

    content_quality_choices = [(-1, "Нет"), (0, "Не очень"), (1, "Да")]
    content_quality = forms.ChoiceField(widget=forms.RadioSelect, choices=content_quality_choices,
                                        label="1. Соответствует ли содержание заявленной теме?")

    knowledge_quality_choices = [(-1, "Отсутствует"), (0, "Поверхностная"), (1, "Средняя"), (2, "Хорошая"),
                                 (3, "Высокая")]
    knowledge_quality = forms.ChoiceField(widget=forms.RadioSelect, choices=knowledge_quality_choices,
                                          label="2. Степень ознакомленности рассказчика с темой семинара, степень понимания материала:")

    presentation_quality_choices = [(-1, "Отсутствует"), (0, "Прослеживается с Трудом"),
                                    (1, "Прослеживается, но существуют явные недочеты"), (2, "Явных недочетов нет"),
                                    (3, "Недочетов нет вовсе")]
    presentation_quality = forms.ChoiceField(widget=forms.RadioSelect, choices=presentation_quality_choices,
                                             label="3. Последовательность и логичность изложения:")

    presentation_quality_2_choices = [(-1, "Тема не раскрыта"), (0, "Тема Раскрыта не полностью"),
                                      (1, "Тема раскрыта не полностью, но присутствуют интересные факты"),
                                      (2, "Тема раскрыта"),
                                      (3, "Тема раскрыта, интересные факты присутствуют")]
    presentation_quality_2 = forms.ChoiceField(widget=forms.RadioSelect, choices=presentation_quality_2_choices,
                                               label=" 4. Степень того, насколько рассказчик раскрыл тему, наличие интересных фактов:")

    presentation_quality_3_choices = [(0, "Нет"), (1, "Да")]
    presentation_quality_3 = forms.ChoiceField(widget=forms.RadioSelect, choices=presentation_quality_3_choices,
                                               label="5.а Считаете ли Вы, что докладчик продемонстрировал неординарные ораторские способности?")

    materials_choices = [(0, "Отсутствует"), (1, "Присутствует"), (2, "Присутствует в разных формах")]
    materials = forms.ChoiceField(widget=forms.RadioSelect, choices=materials_choices,
                                  label="5.б Наличие иллюстирующего материала: ")

    unusual_things_choices = [(0, "Нет или почти нет"), (1, "Да")]
    unusual_things = forms.ChoiceField(widget=forms.RadioSelect, choices=unusual_things_choices,
                                       label="5.в Можете ли Вы отметить что-то необычное в форме проведения семинара?")

    discussion_choices = [(0, "Нет или почти нет"), (1, "Непродолжительное"), (1, "Продолжительное")]
    discussion = forms.ChoiceField(widget=forms.RadioSelect, choices=discussion_choices,
                                   label="6. Вызвал ли семинар обсуждение среди слушателей?")


class P2PKernelForm(forms.Form):
    value = forms.IntegerField(label='Value', required=True, min_value=1)  # consider adding validators here
    description = forms.CharField(max_length=1000, widget=forms.Textarea({'cols': '40', 'rows': '5'}), label='Описание',
                                  required=True)
    receiver_username = ReceiverField(
        queryset=User.objects.filter(groups__name__in=[UserGroups.student.value]).order_by('account__party',
                                                                                           'last_name'),
        required=True,
        empty_label="Выберите получателя", to_field_name="username")
    creator_username = forms.CharField(max_length=200)


class LabKernelForm(forms.Form):
    # TODO add validator that username1 != username2
    value_1 = forms.IntegerField(label='Баксы первому пионеру', required=True, min_value=1)
    value_2 = forms.IntegerField(label='Баксы второму пионеру', required=True, min_value=1)
    receiver_username_1 = ReceiverField(
        queryset=User.objects.filter(groups__name__in=[UserGroups.student.value]).order_by('account__party',
                                                                                           'last_name'),
        required=True,
        empty_label="Первый Пионер", to_field_name="username", label="Первый пионер")
    receiver_username_2 = ReceiverField(
        queryset=User.objects.filter(groups__name__in=[UserGroups.student.value]).order_by('account__party',
                                                                                           'last_name'),
        required=True,
        empty_label="Второй пионер", to_field_name="username",label="Второй пионер")

    description = forms.CharField(max_length=1000, widget=forms.Textarea({'cols': '40', 'rows': '5'}), label='Описание',
                                  required=True)

    date = MyDateField(initial=datetime.date.today, label="Дата cдачи отчета")

    creator_username = forms.CharField(max_length=200)


'''
class RecipientModelChoiceField(ModelChoiceField):
    def label_from_instance(self, account):
        return str(account.otr) + ' ' + (account.long_name())


class SprecialTransForm(forms.Form):
    
    #class Meta:
    #    model = Transaction
    #    fields = ('recipient', 'value', 'description')
    

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


class FineTransForm(forms.Form):
    recipient = RecipientModelChoiceField(queryset=Account.objects.filter(user__groups__name='pioner').order_by('otr',
                                                                                                                'user__last_name'),
                                          label='Пионер')

    type = forms.ModelChoiceField(queryset=TransactionType.objects.all().filter(group1='fine'),
                                  label='Тип штрафа')
    value = forms.IntegerField(label='Сумма штрафа', max_value=2000, min_value=0,
                               help_text='Ну в 90% случаев штрафуют за мат 10 бачей (c)Ахмеджанов')

    description = forms.CharField(label='Пояснение', max_length=1000, widget=forms.Textarea)
'''

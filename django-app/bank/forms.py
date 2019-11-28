# coding=utf-8
import datetime
import string

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet
from django.forms.widgets import ChoiceWidget
from transliterate.utils import _

from bank.constants import UserGroups, AttendanceTypeEnum
from bank.constants.TransactionTypeEnum import TransactionTypeEnum
from bank.models.MoneyType import MoneyType
from bank.models.AttendanceBlock import AttendanceBlock
from bank.models.Attendance import Attendance


# -*- coding: utf-8 -*-
class AtomicTypeField(forms.ModelChoiceField):
    def to_python(self, value):
        return value


class MyDateField(forms.DateField):
    def to_python(self, value):
        s = str(value)
        # try:
        #     datetime.datetime.strptime(s, '%Y-%m-%d')
        # except ValueError:
        #     raise ValidationError('Невозможная дата: %(value)s', params={'value': s})
        return s


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
    place_choices = [(1, "1"), (2, "2"), (3, "3"), (4, "Участник"), (5, "-")]
    place = forms.ChoiceField(widget=PlaceWidget, choices=place_choices, required=False)


class ExamKernelForm(ValueKernelForm):
    value = forms.IntegerField(label='Value', required=False)


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


class DSKernelForm(AttendKernelForm):
    money_type = AtomicTypeField(label="Вид Дежурства",
                                 queryset=MoneyType.objects.filter(
                                     related_transaction_type__name=TransactionTypeEnum.ds.value),
                                 required=True, empty_label=None, to_field_name="name")


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

    discussion_choices = [(0, "Нет или почти нет"), (1, "Непродолжительное"), (2, "Продолжительное")]
    discussion = forms.ChoiceField(widget=forms.RadioSelect, choices=discussion_choices,
                                   label="6. Вызвал ли семинар обсуждение среди слушателей?")

    general_choices = [(-1, "-1"), (0, "0"), (1, "1"), (2, "2"), (3, "3")]
    general_quality = forms.ChoiceField(widget=forms.RadioSelect, choices=general_choices,
                                        label="7. Дополнительные баллы на ваше усмотрение.")


class P2PKernelForm(forms.Form):
    def __init__(self, creator, *args, **kwargs):
        super(P2PKernelForm, self).__init__(*args, **kwargs)
        self.fields['value'] = forms.IntegerField(max_value=creator.account.balance, label="Сумма", min_value=1,
                                                  required=True)
        self.fields['receiver_username'] = ReceiverField(
            queryset=User.objects.filter(groups__name__in=[UserGroups.student.value]).exclude(
                username=creator.username).order_by('account__party',
                                                    'last_name'),
            required=True,
            empty_label="Выберите получателя", to_field_name="username", label="Получатель")

    description = forms.CharField(max_length=1000, widget=forms.Textarea({'cols': '40', 'rows': '5'}),
                                  label='Комментарий',
                                  help_text="Пожалуйста максимально подробно опишите за что вы перечисляете деньги,\
                                   чтобы банкиру и вожатым было проще разобраться и одобрить перевод.",
                                  required=True)
    creator_username = forms.CharField(max_length=200)


class LabKernelForm(forms.Form):
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
        empty_label="Второй пионер", to_field_name="username", label="Второй пионер")

    description = forms.CharField(max_length=1000, widget=forms.Textarea({'cols': '40', 'rows': '5'}), label='Описание',
                                  required=True)

    date = MyDateField(initial=datetime.date.today, label="Дата cдачи отчета")

    creator_username = forms.CharField(max_length=200)

    def clean(self):
        cleaned_data = super(LabKernelForm, self).clean()
        receiver_username_1 = cleaned_data.get("receiver_username_1")
        receiver_username_2 = cleaned_data.get("receiver_username_2")

        if receiver_username_1 and receiver_username_2 and receiver_username_1 == receiver_username_2:
            self.add_error('receiver_username_2', "Пожалуйста выберите разных пионеров как партнеров по лабе")
            self.add_error('receiver_username_1', "Пожалуйста выберите разных пионеров как партнеров по лабе")


class RelativePathField(forms.CharField):
    def validate(self, value):
        super(forms.CharField, self).validate(value)
        allowed = string.ascii_letters + string.digits + "/"
        for c in value:
            if c not in allowed:
                raise ValidationError(
                    _('Недопустимый символ в пути: %(value)s'),
                    params={'value': c},
                )


class UploadFileForm(forms.Form):
    path = RelativePathField(max_length=100, label="Путь",
                             help_text="В пути допускаются только английские буквы цифры и /")
    file = forms.FileField(label="Выберите файл")


class SeminarFormset(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        cleaned_data = self.forms[0].cleaned_data
        receiver_username = cleaned_data.get("receiver")
        date = cleaned_data.get('date')
        block = cleaned_data.get('block')
        attendance_block = AttendanceBlock.objects.get(name=block)
        receiver = User.objects.get(username=receiver_username)
        test_attendance = Attendance(related_transaction=None, receiver=receiver, value=0, type=None,
                                     description='', counted=False, update_timestamp=None, date=date,
                                     attendance_block=attendance_block)
        if not test_attendance.is_valid():
            self.forms[0].add_error('block', "Докладчик уже занимался чем-то в этот блок.\
                            Может быть вы перепутали докладчика или блок? \
                            Если все правильно, то обратитесь пожалуйста к банкиру, он разберется в чем дело.")

        del test_attendance

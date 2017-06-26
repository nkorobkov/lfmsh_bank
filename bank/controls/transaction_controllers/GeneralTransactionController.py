from django.contrib.auth.models import User
from django.forms import formset_factory

from bank.constants import UserGroups, NUM_OF_PARTIES
from bank.forms import GeneralMoneyKernelForm, GeneralMoneyFormSet


class GeneralTransactionController:
    template_url = 'bank/add_trans/trans_add_general_money.html'

    @staticmethod
    def get_form(creator_username):
        students_query = User.objects.filter(groups__name__contains=UserGroups.student.value).order_by('account__party',
                                                                                                       'last_name')
        initial = [
            {'student_name': user.account.long_name(), 'student_party': user.account.party,
             'receiver_username': user.username, 'creator_username': creator_username} for user in students_query]
        general_money_formset = formset_factory(GeneralMoneyKernelForm, formset=GeneralMoneyFormSet,
                                                max_num=len(students_query))
        return general_money_formset(initial=initial)

    @staticmethod
    def process_valid_form(form):
        pass

    @staticmethod
    def get_render_map_update():
        students_query = User.objects.filter(groups__name__contains=UserGroups.student.value)
        endtable = []
        starttable = []
        marker = 0
        for party in range(1, NUM_OF_PARTIES + 1):
            starttable.append(marker+1)
            marker += len(students_query.filter(account__party=party))
            endtable.append(marker)

        return {'markup': {'endtable': endtable, 'starttable': starttable}}

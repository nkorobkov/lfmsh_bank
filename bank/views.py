import ast
import logging
import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest

from bank.controls.TransactionService import TransactionService
from bank.controls.stats_controller import get_student_stats
from bank.helper_functions import get_perm_name, get_students_markup, get_next_missed_lec_penalty
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from .forms import *
from django_tables2 import RequestConfig
from .tables import *
from .constants import *
import time
import pprint

log = logging.getLogger(__name__)


# Create your views here.
@login_required
def index(request):
    log.info(request.user.last_name + ' index')
    student_stats = get_student_stats(request.user)
    transaction_types = TransactionType.objects.all()
    transaction_type_info = [  # TODO change to resolve perm on server
        {"name": t.name, "readable_name": t.readable_name, "create_permission": "bank.create_self_" + t.name} for t in
        transaction_types]
    counters = get_counters_of_user_who_is(request.user, request.user, 'self')
    return render(request, 'bank/indexx.html',
                  {'transaction_type_info': transaction_type_info,
                   'st_stats': student_stats, 'counters': counters})


@login_required
def add_transaction(request, type_name, update_of=None, from_template=None):
    if update_of:
        updated_transaction = get_object_or_404(Transaction, id=update_of)
        if not user_can_update(request, updated_transaction):
            return HttpResponseForbidden()
        if not updated_transaction.type.name == type_name:
            return HttpResponseBadRequest('Transaction type do not match updated transaction type')

    elif not request.user.has_perm(get_perm_name(Actions.create.value, 'self', type_name)):
        log.warning(request.user.get_username() + ' access denied on add trans ' + type_name)
        return HttpResponseForbidden()

    controller = TransactionService.get_controller_for(type_name)
    TransactionFormset = controller.get_blank_form()
    if update_of or from_template:
        source = update_of if update_of else from_template
        initial = json.loads(get_object_or_404(Transaction, id=source).creation_map)
    else:
        initial = controller.get_initial_form_data(request.user.username)
    if request.method == 'POST':
        formset = TransactionFormset(request.POST, initial=initial)
        if formset.is_valid():
            if update_of:
                get_object_or_404(Transaction, id=update_of).substitute()
            created_transaction = controller.get_transaction_from_form_data(formset.cleaned_data, update_of)
            if request.user.has_perm(get_perm_name(Actions.process.value, 'self', type_name)):
                # process transaction if have rights to do so
                created_transaction.process()
            return render(request, 'bank/add/success.html', {'transaction': created_transaction})

    else:  # if GET
        # prepare empty form
        formset = TransactionFormset(initial=initial)
    # if GET or if form was invalid
    render_map = {'formset': formset, 'type_name': type_name, 'update_of': update_of, 'from_template': from_template}
    render_map.update(controller.get_render_map_update())
    return render(request, controller.template_url, render_map)


@login_required()
def decline(request, transaction_id):
    declined_transaction = get_object_or_404(Transaction, id=transaction_id)
    if not user_can_decline(request, declined_transaction):
        return HttpResponseForbidden()
    if request.method == 'POST':
        declined_transaction.decline()
        return render(request, 'bank/decline/decline_success.html', {'transaction': declined_transaction})

    else:  # GET
        return render(request, 'bank/decline/decline_confirm.html', {'transaction': declined_transaction})


@login_required
def my_transactions(request):
    return render(request, 'bank/transaction_lists/self_transactions.html',
                  _get_transactions_of_user_who_is(request.user, request.user, 'self'))


@login_required
def students(request):
    students_data = User.objects.filter(groups__name__contains=UserGroups.student.value).order_by('account__party',
                                                                                                  'last_name')
    render_dict = get_students_markup(students_data)
    render_dict.update({'students': students_data})
    render_dict.update({'can_see_balance': request.user.has_perm(
        get_perm_name(Actions.see.value, UserGroups.student.value, 'balance'))})

    return render(request, 'bank/user_lists/students.html', render_dict)


@login_required
def staff(request):
    staff_data = User.objects.filter(groups__name__contains=UserGroups.staff.value).order_by('last_name')
    render_dict = {'staff': staff_data}
    render_dict.update({'can_see_balance': request.user.has_perm(
        get_perm_name(Actions.see.value, UserGroups.staff.value, 'balance'))})
    return render(request, 'bank/user_lists/staff.html', render_dict)


@login_required()
def user(request, username):
    host = User.objects.get(username=username)
    host_group = host.groups.get(name__in=[UserGroups.staff.value, UserGroups.student.value])
    render_dict = {'host': host}
    render_dict.update(
        {'can_see_balance': request.user.has_perm(get_perm_name(Actions.see.value, host_group.name, 'balance')),
         'can_see_counters': request.user.has_perm(get_perm_name(Actions.see.value, host_group.name, 'attendance'))})
    render_dict.update(_get_transactions_of_user_who_is(request.user, host, host_group.name))
    render_dict.update({'counters': get_counters_of_user_who_is(request.user, host, host_group)})
    return render(request, 'bank/user_page.html', render_dict)


def manage(request, user_group, to_decline=None, to_process=None):
    can_process = request.user.has_perm(
        get_perm_name(Actions.process.value, user_group, 'created_transactions'))
    can_decline = request.user.has_perm(
        get_perm_name(Actions.decline.value, user_group, 'created_transactions'))
    if not (can_decline or can_process):
        return HttpResponseForbidden()

    if to_decline and can_decline:
        transaction = get_object_or_404(Transaction, id=to_decline)
        if transaction.creator.groups.filter(name__in=[user_group]).exists():
            transaction.decline()
        else:
            return HttpResponseForbidden()

    if to_process and can_process:
        get_object_or_404(Transaction, id=to_process).process()

    render_dict = {"transactions": Transaction.objects.filter(creator__groups__name__in=[user_group]).filter(
        state__name=States.created.value)}
    render_dict.update({'can_process': can_process, 'can_decline': can_decline})
    render_dict.update({'user_group': user_group})
    return render(request, 'bank/transaction_lists/manage.html', render_dict)


@permission_required('bank.view_pio_trans_list', login_url='bank:index')
def meta_list(request, trans_id):
    trans = Transaction.objects.get(pk=trans_id)
    if trans.creator != request.user and not request.user.has_perm('del_foreign_trans'):
        return redirect(reverse('bank:index'))
    transactions = trans.meta_link.all()[0].transactions.all()
    # print transactions
    return render(request, 'bank/transaction_lists/my_trans_list_ped.html', {'out_trans': transactions})


@permission_required('bank.add_transaction', login_url='bank:index')
def trans_red(request, trans_id):
    trans = Transaction.objects.get(pk=trans_id)
    if trans.creator != request.user and not request.user.has_perm('bank.del_foreign_trans'):
        return redirect(reverse('bank:index'))
    dec_trans_ok(request, trans_id)  # delete what we have
    print(trans_id)
    # reverse to specific form
    type = trans.type
    if type.name == 'zar':
        return redirect(reverse('bank:add_zaryadka', kwargs={'meta_link_pk': int(trans_id)}))
    if type.name == 'lec':
        return redirect(reverse('bank:add_exam', kwargs={'meta_link_pk': int(trans_id)}))


@permission_required('bank.view_pio_trans_list', login_url='bank:index')
def trans_list(request, username):
    user_group_name = User.objects.get(username=username).groups.filter(name__in=['pioner', 'pedsostav', 'admin'])[
        0].name

    if user_group_name != 'pioner' and not request.user.has_perm('bank.view_ped_trans_list'):
        return redirect(reverse('bank:index'))

    t_user = User.objects.get(username=username)

    in_trans = Transaction.objects.filter(recipient=t_user).order_by('-creation_date')
    out_trans = Transaction.objects.filter(creator=t_user).order_by('-creation_date')

    return render(request, 'bank/transaction_lists/admin_trans_list.html',
                  {'in_trans': in_trans, 'out_trans': out_trans, 'user_group': user_group_name, 'user': t_user})


@permission_required('bank.manage_trans', login_url='bank:index')
def manage_p2p(request):
    if request.method == "POST":

        print((request.POST))

        con_trans = []
        dec_trans = []

        for pk in range(50000):
            if 'c_' + str(pk) in request.POST:
                t = Transaction.objects.get(pk=pk)
                if request.POST['c_' + str(pk)] == 'confirm':
                    print('confirm' + str(t.pk))
                    t.status = TransactionState.objects.get(name='PR')
                    t.count()

                    con_trans.append(t)

                if request.POST['c_' + str(pk)] == 'cancel':
                    print('cancel' + str(t.pk))
                    t.status = TransactionState.objects.get(name='DA')
                    t.save()
                    dec_trans.append(t)

    trans = Transaction.objects.filter(status__name='AD').order_by('creation_date')

    return render(request, 'bank/transaction_lists/admin_p2p_list.html', {'trans': trans})


@permission_required('bank.see_super_table', login_url='bank:index')
def super_table(request):
    table = TransTable(Transaction.objects.all(), order_by='-creation_date')
    RequestConfig(request).configure(table)
    table.paginate(per_page=500)

    return render(request, 'bank/s_table.html', {'trans': table})


def media(request):
    return redirect('/media/')


def _get_transactions_of_user_who_is(user, target_user, group):
    created_transactions = []
    received_money = []
    received_counters = []
    if user.has_perm(get_perm_name(Actions.see.value, group, 'created_transactions')):
        for trans in Transaction.objects.filter(creator=target_user).order_by('-creation_timestamp').all():
            trans_info = {'transaction': trans}
            if group == 'self':
                target_transaction_identifier = trans.type.name
            else:
                target_transaction_identifier = 'created_transactions'
            trans_info.update(
                {'update': user.has_perm(get_perm_name(Actions.update.value, group,
                                                       target_transaction_identifier)) and trans.state.possible_transitions.filter(
                    name=States.substituted.value).exists()})
            trans_info.update(
                {'decline': user.has_perm(get_perm_name(Actions.decline.value, group,
                                                        target_transaction_identifier)) and trans.state.possible_transitions.filter(
                    name=States.declined.value).exists()})
            trans_info.update(
                {'create': user.has_perm(get_perm_name(Actions.create.value, group, target_transaction_identifier))})
            created_transactions.append(trans_info)

    if user.has_perm(get_perm_name(Actions.see.value, group, 'received_transactions')):
        received_money = Money.objects.filter(receiver=target_user).filter(counted=True).order_by('-creation_timestamp')
        received_counters = Attendance.objects.filter(receiver=target_user).filter(counted=True).order_by(
            '-creation_timestamp')
    return {'created_transactions': created_transactions, 'received_counters': received_counters,
            'received_money': received_money}


def user_can_update(request, updated_transaction):
    """
    can update only self transactions with rights
    """
    if not updated_transaction.state.possible_transitions.all().filter(name=States.substituted.value).exists():
        return False
    if updated_transaction.creator.username == request.user.username:
        if request.user.has_perm(get_perm_name(Actions.update.value, 'self', updated_transaction.type.name)):
            return True
    else:
        return False


def user_can_decline(request, updated_transaction):
    if not updated_transaction.state.possible_transitions.all().filter(name=States.declined.value).exists():
        return False
    if updated_transaction.creator.username == request.user.username:
        if request.user.has_perm(get_perm_name(Actions.decline.value, 'self', updated_transaction.type.name)):
            return True
    else:
        if request.user.has_perm(get_perm_name(Actions.decline.value, updated_transaction.creator.groups.get(
                name__in=[UserGroups.staff.value, UserGroups.student.value, UserGroups.admin.value]).name,
                                               'created_transaction')):
            return True
    return False


def get_counters_of_user_who_is(user, target_user, group):
    if not user.has_perm(get_perm_name(Actions.see.value, group, "attendance")):
        return None

    all_counters = Attendance.objects.filter(receiver=target_user).filter(counted=True)
    info = {"study_needed": STUDY_NEEDED, "fac_pass_needed": FAC_PASS_NEEDED.get(target_user.account.grade),
            "lab_pass_needed": LAB_PASS_NEEDED.get(target_user.account.grade)}
    counters_val = {}
    for counter_type in AttendanceType.objects.all():
        counter_sum = sum([c.value for c in all_counters.filter(type=counter_type)])
        counters_val.update({counter_type.name: int(counter_sum)})
    info.update({"study": counters_val.get(AttendanceTypeEnum.fac_attend.value) + counters_val.get(
        AttendanceTypeEnum.seminar_attend.value)})
    info.update(
        {"next_missed_lec_fine": get_next_missed_lec_penalty(counters_val.get(AttendanceTypeEnum.lecture_miss.value))})
    return {"val": counters_val, "info": info}

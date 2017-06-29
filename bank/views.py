import logging
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden

from bank.controls.TransactionService import TransactionService
from bank.helper_functions import get_student_stats, get_perm_name, get_students_markup
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from .forms import *
from django_tables2 import RequestConfig
from .tables import *
from . import helper_functions as hf
from .constants import *
import time
import pprint

log = logging.getLogger(__name__)


# Create your views here.
@login_required
def index(request):
    log.info(request.user.last_name + ' index')
    student_stats = get_student_stats()
    transaction_types = TransactionType.objects.all()
    transaction_type_info = [
        {"name": t.name, "readable_name": t.readable_name, "create_permission": "bank.create_self_" + t.name} for t in
        transaction_types]
    return render(request, 'bank/indexx.html',
                  {'transaction_type_info': transaction_type_info,
                   'st_stats': student_stats})


@login_required
def add_transaction(request, type_name):
    if not request.user.has_perm(get_perm_name(Actions.create.value, 'self', type_name)):
        log.warning(request.user + ' access denied on add trans ' + type_name)
        return HttpResponseForbidden()

    controller = TransactionService.get_controller_for(type_name)
    TransactionFormset = controller.get_blank_form()
    initial = controller.get_initial_form_data(request.user.username)

    if request.method == 'POST':
        formset = TransactionFormset(request.POST, initial=initial)
        if formset.is_valid():
            created_transaction = controller.get_transaction_from_form_data(formset.cleaned_data)
            if request.user.has_perm(get_perm_name(Actions.process.value, 'self', type_name)):
                # process transaction if have rights to do so
                created_transaction.process()
            return render(request, 'bank/add_trans/success.html', {'transaction': created_transaction})

    else:  # if GET
        # prepare empty form
        formset = TransactionFormset(initial=initial)
    # if GET or if form was invalid
    render_map = {'formset': formset, 'type_name': type_name}
    render_map.update(controller.get_render_map_update())
    return render(request, controller.template_url, render_map)


@login_required
def my_transactions(request):
    return render(request, 'bank/transaction_lists/self_transactions.html',
                  _get_transactions_of_user_who_is(request.user, 'self'))


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
    render_dict.update(_get_transactions_of_user_who_is(host, host_group.name))
    return render(request, 'bank/user_page.html', render_dict)


@login_required()
def dec_trans(request, trans_id):
    print('decline page')

    trans = Transaction.objects.get(pk=trans_id)
    if not trans.recipient:
        to_del = trans.meta_link.all()[0].transactions.all()
    else:
        to_del = [trans]
    if trans.creator != request.user and not request.user.has_perm('bank.del_foreign_trans'):
        return redirect(reverse('bank:index'))

    return render(request, 'bank/dec_trans/trans_dec_confirm.html', {'trans': to_del, 'meta': trans_id})


@login_required
def dec_trans_ok(request, trans_id):
    user_group_name = request.user.groups.filter(name__in=['pioner', 'pedsostav', 'admin'])[0].name
    trans = Transaction.objects.get(pk=trans_id)
    if trans.creator != request.user and not request.user.has_perm('bank.del_foreign_trans'):
        return redirect(reverse('bank:index'))
    if not trans.recipient:
        to_del = trans.meta_link.all()[0].transactions.all()
    else:
        to_del = [trans]
    if request.user.has_perm('bank.del_foreign_trans') and to_del[0].creator != request.user:

        st = TransactionState.objects.get(name='DA')

    else:
        st = TransactionState.objects.get(name='DC')
    for t in to_del:
        print('decline of trans happening')
        t.cancel()
        t.status = st
        t.save()

        trans.status = st
        trans.save()

    return render(request, 'bank/dec_trans/trans_dec_ok.html', {'transactions': to_del})


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


def _get_transactions_of_user_who_is(user, group):
    created_transactions = []
    received_money = []
    received_counters = []
    if user.has_perm(get_perm_name(Actions.see.value, group, 'created_transactions')):
        # TODO: order by time somehow
        created_transactions = Transaction.objects.filter(creator=user)

    if user.has_perm(get_perm_name(Actions.see.value, 'self', 'received_transactions')):
        received_money = Money.objects.filter(receiver=user).order_by('-creation_timestamp')
        received_counters = Attendance.objects.filter(receiver=user).order_by('-creation_timestamp')

    return {'created_transactions': created_transactions, 'received_counters': received_counters,
            'received_money': received_money}

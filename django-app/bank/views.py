import logging
import json
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from os import path
import os
from bank.controls.TransactionService import TransactionService
from bank.controls.stats_controller import get_student_stats, get_report_student_stats, get_counters_of_user_who_is
from bank.helper_functions import get_perm_name, get_students_markup
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, permission_required

from bank.models.Money import Money
from bank.models.TransactionType import TransactionType
from bank.models.Transaction import Transaction
from main.settings import MEDIA_ROOT
from .forms import *
from django_tables2 import RequestConfig
from .tables import *
from .constants import *

log = logging.getLogger("bank_log")


# Create your views here.
@login_required
def index(request):
    log.info("index page request from {}".format(request.user.account.long_name()))
    student_stats = get_student_stats(request.user)
    transaction_types = TransactionType.objects.all()
    transaction_type_info = [
        {"name": t.name, "readable_name": t.readable_name,
         "can_create": request.user.has_perm(get_perm_name(Actions.create.value, "self", t.name))} for t in
        transaction_types]
    counters = get_counters_of_user_who_is(request.user, request.user, 'self')
    return render(request, 'bank/indexx.html',
                  {'transaction_type_info': transaction_type_info,
                   'st_stats': student_stats, 'counters': counters})


@login_required
def add_transaction(request, type_name, update_of=None, from_template=None):
    if not request.user.has_perm(get_perm_name(Actions.create.value, 'self', type_name)):
        log.warning(request.user.get_username() + ' access denied on add trans ' + type_name)
        return HttpResponseForbidden()

    if update_of or from_template:
        source = update_of if update_of else from_template
        updated_transaction = get_object_or_404(Transaction, id=source)

        if update_of and not user_can_update(request, updated_transaction):
            return HttpResponseForbidden("У вас нет прав на изменение этой транзакции")
        if from_template and not user_can_use_template(request, updated_transaction):
            return HttpResponseForbidden("Эту транзакцию нельзя использовать как шаблон")
        if not updated_transaction.type.name == type_name:
            return HttpResponseBadRequest("Тип транзакции из шаблона не совпадает с типом указанным в адресной строке")

    controller = TransactionService.get_controller_for(type_name)
    TransactionFormset = controller.get_blank_form(creator_username=request.user.username)
    if update_of or from_template:
        source = update_of if update_of else from_template
        initial = json.loads(get_object_or_404(Transaction, id=source).creation_map)
    else:
        initial = controller.get_initial_form_data(request.user.username)
    if request.method == 'POST':
        formset = TransactionFormset(request.POST, initial=initial)
        if formset.is_valid():
            if update_of:
                try:
                    get_object_or_404(Transaction, id=update_of).substitute()
                except AttributeError:
                    raise AttributeError('Попытка изменить транзакцию которую нельзя изменить')
            created_transaction = controller.get_transaction_from_form_data(formset.cleaned_data, update_of)
            log.info("Valid add transaction from {}, update={}, transaction={}".format(request.user.account.long_name(),
                                                                                       update_of, created_transaction))
            if request.user.has_perm(get_perm_name(Actions.process.value, 'self', type_name)):
                # process transaction if have rights to do so
                created_transaction.process()  # update should be inside.
            return render(request, 'bank/add/success.html', {'transaction': created_transaction,
                                                             'can_use_tmp': user_can_use_template(request,
                                                                                                  created_transaction),
                                                             'can_update': user_can_update(request,
                                                                                           created_transaction),
                                                             'can_decline': user_can_decline(request,
                                                                                             created_transaction)})

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
    log.info(
        "Decline transaction from {}, transaction={}".format(request.user.account.long_name(),
                                                             declined_transaction))

    if not user_can_decline(request, declined_transaction):
        return HttpResponseForbidden("У вас нет прав отменить эту транзакцию")
    if request.method == 'POST':
        declined_transaction.decline()
        return render(request, 'bank/decline/decline_success.html', {'transaction': declined_transaction,
                                                                     'can_use_tmp': user_can_use_template(request,
                                                                                                          declined_transaction)})

    else:  # GET
        return render(request, 'bank/decline/decline_confirm.html', {'transaction': declined_transaction})


@login_required
def my_transactions(request):
    return render(request, 'bank/transaction_lists/self_transactions.html',
                  _get_transactions_of_user_who_is(request.user, request.user, 'self'))


@login_required
def get_transaction_HTML(request):
    transaction_id = request.GET.get('transaction_id', -1)
    viewer_role = request.GET.get('viewer_role', -1)
    transaction = Transaction.objects.get(id=transaction_id)  # if there is no transaction it fails, but it's ok.

    group = 'self' if request.user == transaction.creator else get_used_user_group(transaction.creator)
    if not request.user.has_perm(get_perm_name(Actions.see.value, group, 'created_transactions')):
        return HttpResponseForbidden("У вас нет прав на просмотр этой транзакции")

    html = loader.render_to_string('bank/transaction_lists/transaction.html',
                                   {'transaction': transaction, 'viewer_role': viewer_role})
    output_data = {'transaction_HTML': html}
    return JsonResponse(output_data)


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
    host_group = get_used_user_group(host)
    render_dict = {'host': host}
    render_dict.update(
        {'can_see_balance': request.user.has_perm(get_perm_name(Actions.see.value, host_group.name, 'balance')),
         'can_see_counters': request.user.has_perm(get_perm_name(Actions.see.value, host_group.name, 'attendance'))})
    render_dict.update(_get_transactions_of_user_who_is(request.user, host, host_group.name))
    render_dict.update({'counters': get_counters_of_user_who_is(request.user, host, host_group)})
    avatar_url = "bank/avatars/{} {}.jpg".format(host.last_name, host.first_name) if USE_PICS else DEFAULT_PIC_PATH
    render_dict.update({'avatar_url': avatar_url})
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
            return HttpResponseForbidden("У вас нет прав отменить эту транзакцию")

    if to_process and can_process:
        transaction = get_object_or_404(Transaction, id=to_process)
        if transaction.creator.groups.filter(name__in=[user_group]).exists():
            transaction.process()
        else:
            return HttpResponseForbidden("У вас нет прав начислить эту транзакцию")

    render_dict = {"transactions": Transaction.objects.filter(creator__groups__name__in=[user_group]).filter(
        state__name=States.created.value)}
    render_dict.update({'can_process': can_process, 'can_decline': can_decline})
    render_dict.update({'user_group': user_group})
    return render(request, 'bank/transaction_lists/manage.html', render_dict)


@permission_required(get_perm_name(Actions.see.value, UserGroups.staff.value, "created_transactions"),
                     login_url='bank:index')
def monitor_table(request):
    table = TransTable(Transaction.objects.all(), order_by='-date_created')
    RequestConfig(request).configure(table)
    table.paginate(per_page=200)
    return render(request, 'bank/monitor_table.html', {'trans': table})


@permission_required(get_perm_name(Actions.upload.value, "self", "files"), login_url='bank:index')
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            local_path = form.cleaned_data['path'].strip('/')
            user_path = path.join(MEDIA_ROOT, local_path, f.name)
            log.info("file uploaded by {},path={}".format(request.user.account.long_name(), user_path))
            os.makedirs(path.dirname(user_path), exist_ok=True)
            with open(user_path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            return render(request, 'bank/files/success_upload.html', {"filename": f.name})
    else:
        form = UploadFileForm(initial={"path": request.user.username + "/"})
    return render(request, 'bank/files/file_upload.html', {'form': form})


def report(request):
    render_dict = get_report_student_stats(request.user)
    students_query = User.objects.filter(groups__name__contains=UserGroups.student.value)
    render_dict.update(get_students_markup(students_query))
    return render(request, 'bank/report.html', render_dict)


def study_stats(request):
    # TODO: rework templates
    render_dict = get_report_student_stats(request.user)
    students_query = User.objects.filter(groups__name__contains=UserGroups.student.value)
    render_dict.update(get_students_markup(students_query))
    return render(request, 'bank/study_stats.html', render_dict)


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
    if not updated_transaction.can_be_transitioned_to(States.substituted.value):
        return False
    if updated_transaction.creator.username == request.user.username:
        return request.user.has_perm(get_perm_name(Actions.update.value, 'self', updated_transaction.type.name))
    else:
        return False


def user_can_use_template(request, template_trans):
    if template_trans.creator.username == request.user.username:
        return request.user.has_perm(get_perm_name(Actions.create.value, 'self', template_trans.type.name))
    else:
        return False


def user_can_decline(request, updated_transaction):
    if not updated_transaction.can_be_transitioned_to(States.declined.value):
        log.warning(
            request.user.account.long_name() + " cant decline transaction because transaction can not be transitioned to declined state")
        return False
    if updated_transaction.creator.username == request.user.username:
        if request.user.has_perm(get_perm_name(Actions.decline.value, 'self', updated_transaction.type.name)):
            return True
        log.warning(
            request.user.account.long_name() + " cant decline transaction because user do not have rights to decline self created " + updated_transaction.type.name)

    else:

        if request.user.has_perm(get_perm_name(Actions.decline.value, updated_transaction.creator.groups.get(
                name__in=PERMISSION_RESPONSIBLE_GROUPS).name,
                                               'created_transactions')):
            return True
        log.warning(
            request.user.account.long_name() + " is not owner of transaction and do not have rights to decline " + updated_transaction.creator.groups.get(
                name__in=PERMISSION_RESPONSIBLE_GROUPS).name + " group. but tries to decline it")

    return False


def get_used_user_group(user):
    group = user.groups.get(name__in=[UserGroups.staff.value, UserGroups.student.value])
    return group

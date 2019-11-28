import csv
import json

import logging
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from bank.constants import Actions, UserGroups
from bank.constants.BankAPIExeptions import *
from bank.controls.TransactionService import TransactionService
from bank.controls.stats_controller import get_counters_of_user_who_is
from bank.helper_functions import get_perm_name, TransactionTypeEnum
from bank.models.TransactionType import TransactionType
from bank.models.Money import Money
from bank.models.Attendance import Attendance

log = logging.getLogger("bank_api_log")


@csrf_exempt
@login_required()
def get_user_transactions(request):
    user = request.user
    log.info('api user info call from {}'.format(user.account.long_name()))

    if not (user.has_perm(get_perm_name(Actions.see.value, "self", "balance")) and user.has_perm(
            get_perm_name(Actions.see.value, "self", "attendance"))):
        return HttpResponseForbidden("user do not have perm to see this info")

    data = {"balance": user.account.balance,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "balance_changes": [t.to_python() for t in user.account.get_all_money()],
            "counters": [t.to_python() for t in user.received_attendance.all()],
            "counters_value": get_counters_of_user_who_is(user, user, 'self')}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
@login_required()
def add_transaction(request):
    try:
        transaction = make_transaction(request)
    except BankAPIExeption as e:
        return HttpResponse(json.dumps({'error': {'code': e.code, 'message': e.message}}),
                            content_type='application/json', status=400)
    return HttpResponse(json.dumps(transaction.to_python()),
                        content_type='application/json')


@csrf_exempt
def get_students(request):
    students_data = User.objects.filter(groups__name__contains=UserGroups.student.value).order_by('account__party',
                                                                                                  'last_name')
    data = [u.account.full_info_as_map(True) for u in students_data]
    return HttpResponse(json.dumps(data), content_type='application/json')


def make_transaction(request):
    user = request.user
    log.info('api add transaction call from {}'.format(user.account.long_name()))

    trans_data = json.loads(str(request.body, 'utf-8'))

    # if invalid trans type -- return illegal request
    if not trans_data_is_valid(trans_data):
        raise TransactionTypeNotRecognized()

    # Extract transaction type.
    type_name = TransactionType.objects.get(name=trans_data.get("transaction_type")).name

    # check if request owner equals transaction creator
    if trans_data.get('creator') != request.user.username:
        raise CreatorDoNotMatchRequestOwner()

    # check user can create such transactions
    if not request.user.has_perm(get_perm_name(Actions.create.value, 'self', type_name)):
        log.warning(request.user.get_username() + ' access denied on add trans ' + type_name + 'through API')
        raise CantCreateThisType(type_name)

    # if can -- call transaction controller to create transaction instance from request body
    controller = TransactionService.get_controller_for(type_name)
    transaction = controller.build_transaction_from_api_request(trans_data)
    # check if user can process this transaction
    if request.user.has_perm(get_perm_name(Actions.process.value, 'self', type_name)):
        # process transaction if have rights to do so
        transaction.process()
        # if can -- process, return success result.

    return transaction


@csrf_exempt
def get_session(request):
    if request.method == "POST":
        try:
            request_data = json.loads(str(request.body, 'utf-8'))
            username = request_data['login']
            password = request_data['password']
        except(KeyError, TypeError):
            return HttpResponseBadRequest()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
        auth_success = user is not None
        data = {
            "auth_success": auth_success,
            "session_id": request.session.session_key,
        }
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponseBadRequest()


@csrf_exempt
def get_students_money(request):
    if not request.user.has_perm(get_perm_name(Actions.see.value, UserGroups.staff.value, "created_transactions")):
        return HttpResponseForbidden()

    return get_csv_for_model(Money, "money")


@csrf_exempt
def get_students_counters(request):
    if not request.user.has_perm(get_perm_name(Actions.see.value, UserGroups.staff.value, "created_transactions")):
        return HttpResponseForbidden()

    return get_csv_for_model(Attendance, "counters")


def get_csv_for_model(model, file_name):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + file_name + '.csv"'
    writer = csv.writer(response)
    writer.writerow(model.objects.all().first().full_info_headers_as_list())
    for inst in model.objects.all():
        writer.writerow(inst.full_info_as_list())
    return response


def trans_data_is_valid(trans_data):
    if "transaction_type" in trans_data.keys():
        type_name = trans_data.get("transaction_type")
        if type_name in TransactionTypeEnum.__members__:
            return 1
    return 0

import csv
import json

import logging
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from bank.constants import Actions, UserGroups
from bank.controls.stats_controller import get_counters_of_user_who_is
from bank.helper_functions import get_perm_name
from bank.models import Money, Attendance

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

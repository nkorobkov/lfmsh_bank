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
from bank.models import Money

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
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students_money.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ['value', 'creator', 'creation_date', 'type', 'desc', 'receiver', 'general_group', 'local_group', 'counted',
         'update_date', 'receiver_username'])

    for money in Money.objects.filter(counted=True,
                                      related_transaction__creator__groups__name__in=[UserGroups.staff.value, UserGroups.admin.value]):
        mon_dic = money.to_python()

        writer.writerow([mon_dic['value'], mon_dic['creator'],mon_dic['creation_timestamp'],mon_dic['type'],mon_dic['description'],mon_dic['receiver'],mon_dic['general_group'],mon_dic['local_group'],mon_dic['counted'],mon_dic['update_timestamp'], money.receiver.username])

    return response

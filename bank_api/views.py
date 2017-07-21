import json

from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def get_user_transactions(request):
    user = request.user
    if not user.is_authenticated():
        return HttpResponseForbidden()

    data = {"balance": user.account.balance,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "balance_changes": [t.to_python() for t in user.account.get_all_money()],
            "counters": [t.to_python() for t in user.received_attendance.all()]}
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

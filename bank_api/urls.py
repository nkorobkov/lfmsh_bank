from django.conf.urls import url

from bank_api import views

app_name = 'bank_api'

urlpatterns = [
    url(r'^user/$', views.get_user_transactions, name='user'),
    url(r'^add_transaction/$', views.add_transaction, name='add_transaction'),
    url(r'^auth/$', views.get_session, name='auth'),
    url(r'^money/$', views.get_students_money, name='money'),
    url(r'^counters/$', views.get_students_counters, name='counters'),
    url(r'^students/$', views.get_students, name='students')
]

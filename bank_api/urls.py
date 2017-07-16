from django.conf.urls import url

from bank_api import views

urlpatterns = [
    url(r'^user/$', views.get_user_transactions, name='user'),
    url(r'^auth/$', views.get_session, name='auth')
]
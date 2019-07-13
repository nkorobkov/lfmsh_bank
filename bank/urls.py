from django.conf.urls import url
from django.contrib.auth import views as auth_views

from bank import views

app_name = 'bank'


urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^login/$', auth_views.LoginView.as_view(), {'template_name': 'bank/login.html', },
        name='login'),

    url(r'^my_transactions/$', views.my_transactions, name='my_transactions'),
    url(r'^getTransactionHTML/$', views.get_transaction_HTML, name='get_transaction_HTML'),


    url(r'^students$', views.students, name='students'),
    url(r'^staff$', views.staff, name='staff'),
    url(r'^user/(?P<username>.+)/$', views.user, name='user'),

    url(r'^add_transaction/(?P<type_name>[^/]+)/tmp(?P<from_template>[0-9]+)/$', views.add_transaction,
        name='add_transaction_from_template'),
    url(r'^add_transaction/(?P<type_name>[^/]+)/upd(?P<update_of>[0-9]+)/$', views.add_transaction,
        name='update_transaction'),
    url(r'^add_transaction/(?P<type_name>.+)/$', views.add_transaction, name='add_transaction'),

    url(r'^decline/(?P<transaction_id>[0-9]+)/$', views.decline, name='decline'),

    url(r'^manage/(?P<user_group>[a-zA-z]+)/$', views.manage, name='manage'),
    url(r'^manage/(?P<user_group>[a-zA-z]+)/pr(?P<to_process>[0-9]+)$', views.manage, name='manage_process'),
    url(r'^manage/(?P<user_group>[a-zA-z]+)/dc(?P<to_decline>[0-9]+)$', views.manage, name='manage_decline'),

    url(r'^report/$', views.report, name='report'),
    url(r'^study_stats/$', views.study_stats, name='study_stats'),

    url(r'^upload/$', views.upload_file, name='upload'),

    url(r'^media/$', views.media, name='media'),

    url(r'^monitor_table/$', views.monitor_table, name='monitor_table'),
]
'''
        url(r'^trans_list/(?P<username>.+)/$', views.trans_list, name='trans_list'),
        url(r'^meta_list/(?P<trans_id>.+)/$', views.meta_list, name='meta_list'),

        url(r'^trans_red/(?P<trans_id>.+)/$', views.trans_red, name='trans_red'),

        url(r'manage_p2p', views.manage_p2p, name='manage_p2p'),

        url(r'^super_table/$', views.super_table, name='super_table'),
    '''
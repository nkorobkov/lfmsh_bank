from django.conf.urls import patterns, url

from bank import views
from helper_functions import PionerAutocomplete

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),

                       url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
                       url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'bank/login.html',},
                           name='login'),


                       url(r'^my_trans/$', views.show_my_trans, name='my_trans'),
                       url(r'^my_att/$', views.show_my_att, name='my_att'),

                       url(r'^all_acc$', views.all_pioner_accounts, name='all_acc'),
                       url(r'^all_acc_ped$', views.all_ped_accounts, name='all_acc_ped'),

                       url(r'^add_trans/special/$', views.add_special, name='add_special'),
                       url(r'^add_trans/mass_special/$', views.add_mass_special, name='add_mass_special'),

                       url(r'^add_trans/zaryadka/(?P<meta_link_pk>[0-9]+)', views.add_zaryadka, name='add_zaryadka'),
                       url(r'^add_trans/zaryadka/', views.add_zaryadka, name='add_zaryadka'),


                       url(r'^add_trans/sem/', views.add_sem, name='add_sem'),
                       url(r'^add_trans/p2p/', views.add_p2p, name='add_p2p'),
                       url(r'^add_trans/fac/', views.add_fac, name='add_fac'),
                       url(r'^add_trans/lab/', views.add_lab, name='add_lab'),
                       url(r'^add_trans/activity/', views.add_activity, name='add_activity'),
                       url(r'^add_trans/fine/', views.add_fine, name='add_fine'),
                       url(r'^add_trans/lec/', views.add_lec, name='add_lec'),
                       url(r'^add_trans/fac_att/', views.add_fac_att, name='add_fac_att'),
                       url(r'^add_trans/exam/(?P<meta_link_pk>[0-9]+)', views.add_exam, name='add_exam'),
                       url(r'^add_trans/exam/', views.add_exam, name='add_exam'),


                       url(r'^dec_trans/(?P<trans_id>[0-9]+)/$', views.dec_trans, name='trans_dec'),
                       url(r'^dec_trans_ok/(?P<trans_id>[0-9]+)/$', views.dec_trans_ok, name='trans_dec_ok'),

                       url(r'^trans_list/(?P<username>.+)/$', views.trans_list, name='trans_list'),
                       url(r'^meta_list/(?P<trans_id>.+)/$', views.meta_list, name='meta_list'),

                       url(r'^trans_red/(?P<trans_id>.+)/$', views.trans_red, name='trans_red'),

                       url(r'manage_p2p', views.manage_p2p, name='manage_p2p'),

                       url(r'^pioner-autocomplete/$', PionerAutocomplete.as_view(), name='pioner-autocomplete'),
                       url(r'^super_table/$', views.super_table, name='super_table'),
					   url(r'^media/$', views.media, name='media'),

                       )


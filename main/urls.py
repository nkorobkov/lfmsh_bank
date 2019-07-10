from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', admin.site.urls),
    url(r'^bank/', include('bank.urls', namespace='bank')),
    url(r'^bank_api/', include('bank_api.urls', namespace='bank_api'))

]

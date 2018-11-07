"""snowland_astardownload URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from . import settings
from django.views.static import serve
# from django.contrib import admin
# import xadmin
from django.contrib import admin
from astardownload.views import *
from django.views import defaults
from django.views.static import serve
# admin.autodiscover()

urlpatterns = [
    url('admin/', admin.site.urls),
    url(r'^$', index),
    url(r'^favicon.ico', favicon),
    url(r'^accounts/login/$', alert_login),
    url(r'^index$', index),
    url(r'^register$', do_register),
    url(r'^upload$', do_upload),
    url(r'^downloadlist$', downloadlist),
    url(r'^downloaditem$', downloaditem),
    url(r'^download$', do_download),
    url(r'^get_code$', get_code),
    url(r'^login$', do_login),
    url(r'^zone$', myzone),
    url(r'^search$', do_search),
    url(r'^aboutus$', do_aboutus),
    url(r'^vip$', do_vip),
    url(r'^logout$', do_logout),
    url(r'^editInfo$', editInfo),
]


handler400 = defaults.bad_request
handler403 = defaults.permission_denied
handler404 = defaults.page_not_found
handler500 = defaults.server_error

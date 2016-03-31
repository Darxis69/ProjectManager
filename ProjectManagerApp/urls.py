from django.conf.urls import url

from ProjectManagerApp.views import LoginFormView
from . import views

urlpatterns = {
    url(r'^account/login/$', LoginFormView.as_view(), name='login'),
    url(r'^account/logout/$', views.logout, name='logout'),
}

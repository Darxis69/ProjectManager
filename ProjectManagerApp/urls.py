from django.conf.urls import url

from ProjectManagerApp.views import LoginFormView, AccountCreateFormView
from . import views

urlpatterns = {
    url(r'^account/login/$', LoginFormView.as_view(), name='login'),
    url(r'^account/logout/$', views.logout, name='logout'),
    url(r'^account/create/$', AccountCreateFormView.as_view(), name="account_create")
}

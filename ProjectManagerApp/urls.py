from django.conf.urls import url

from ProjectManagerApp.views import LoginFormView
from . import views

urlpatterns = {
    url(r'^login/$', LoginFormView.as_view(), name='login'),
    url(r'^logout/$', views.logout, name='logout'),
}

from django.conf.urls import url

from ProjectManagerApp.views import LoginFormView

urlpatterns = {
    url(r'^login/$', LoginFormView.as_view(), name='login'),
}

from django.conf.urls import url

from ProjectManagerApp.views import LoginFormView, AccountCreateFormView, ProjectCreateFormView, IndexView, \
    TeamCreateFormView, TeamListView, ProjectListView
from . import views

urlpatterns = {
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^index/$', IndexView.as_view(), name='index'),
    url(r'^account/login/$', LoginFormView.as_view(), name='login'),
    url(r'^account/logout/$', views.logout, name='logout'),
    url(r'^account/create/$', AccountCreateFormView.as_view(), name="account_create"),
    url(r'^projects/$', ProjectListView.as_view(), name="project_list"),
    url(r'^projects/create/$', ProjectCreateFormView.as_view(), name="project_create"),
    url(r'^projects/delete/$', views.project_delete, name="project_delete"),
    url(r'^teams/$', TeamListView.as_view(), name="team_list"),
    url(r'^teams/create/$', TeamCreateFormView.as_view(), name="team_create"),
    url(r'^teams/join/$', views.team_join, name="team_join"),
    url(r'^teams/leave/$', views.team_leave, name="team_leave")
}

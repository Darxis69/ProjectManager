from django.conf.urls import url

from ProjectManagerApp.views import LoginFormView, AccountCreateFormView, ProjectCreateFormView, IndexView, \
    TeamCreateFormView, TeamListView, ProjectListView
from . import views

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index_url'),
    url(r'^index/$', IndexView.as_view(), name='index_url'),
    url(r'^account/login/$', LoginFormView.as_view(), name='account_login_url'),
    url(r'^account/logout/$', views.logout, name='account_logout_url'),
    url(r'^account/create/$', AccountCreateFormView.as_view(), name="account_create_url"),
    url(r'^projects/$', ProjectListView.as_view(), name="projects_list_url"),
    url(r'^projects/create/$', ProjectCreateFormView.as_view(), name="project_create_url"),
    url(r'^projects/join/$', views.project_join, name="project_join_url"),
    url(r'^projects/delete/$', views.project_delete, name="project_delete_url"),
    url(r'^teams/$', TeamListView.as_view(), name="teams_list_url"),
    url(r'^teams/create/$', TeamCreateFormView.as_view(), name="team_create_url"),
    url(r'^teams/join/$', views.team_join, name="team_join_url"),
    url(r'^teams/leave/$', views.team_leave, name="team_leave_url")
]

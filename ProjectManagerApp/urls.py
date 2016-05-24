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
    url(r'^account/details/$', views.AccountDetailsView.as_view(), name="account_details_url"),
    url(r'^account/delete/$', views.delete_account, name='account_delete_url'),
    url(r'^account/changeEmail/$', views.AccountChangeEmailFormView.as_view(), name="account_change_email_url"),
    url(r'^account/changePassword/$', views.AccountChangePasswordFormView.as_view(), name="account_change_password_url"),
    url(r'^projects/$', ProjectListView.as_view(), name="projects_list_url"),
    url(r'^projects/create/$', ProjectCreateFormView.as_view(), name="project_create_url"),
    url(r'^projects/join/$', views.project_join, name="project_join_url"),
    url(r'^projects/leave/$', views.project_leave, name="project_leave_url"),
    url(r'^projects/delete/$', views.project_delete, name="project_delete_url"),
    url(r'^projects/details/(?P<id>[0-9]+)/$', views.ProjectDetailsView.as_view(), name="project_details_url"),
    url(r'^projects/edit/$', views.ProjectEditFormView.as_view(), name="project_edit_url"),
    url(r'^teams/$', TeamListView.as_view(), name="teams_list_url"),
    url(r'^teams/create/$', TeamCreateFormView.as_view(), name="team_create_url"),
    url(r'^teams/assign/$', views.team_assign, name="team_assign_url"),
    url(r'^teams/join/$', views.team_join, name="team_join_url"),
    url(r'^teams/leave/$', views.team_leave, name="team_leave_url"),
    url(r'^teams/details/$', views.TeamDetailsView.as_view(), name="team_details_url"),
    url(r'^.*/$', views.handler404, name='error_404_url'),
]

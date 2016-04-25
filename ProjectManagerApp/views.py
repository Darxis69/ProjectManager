from django.contrib.auth import authenticate as auth_authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import FormView
from django.views.generic import TemplateView

from ProjectManagerApp.exceptions import MustBeStudent, UserAlreadyInTeam, UserNotInTeam, MustBeTeacher, \
    ProjectHasAssignedTeam
from ProjectManagerApp.forms import LoginForm, AccountCreateForm, ProjectCreateForm, TeamCreateForm
from ProjectManagerApp.models import Project, Teacher, Student, Team
from ProjectManagerApp.services import user_join_team, user_create_team, user_team_leave, user_delete_project, \
    user_create_project, user_team_join_project


class AccountCreateFormView(FormView):
    template_name = 'account/create.html'
    form_class = AccountCreateForm

    def get_context_data(self, **kwargs):
        return self.create_context_data(AccountCreateForm(self.request.POST)
                                        if self.request.method == "POST" else AccountCreateForm())

    def create_context_data(self, account_create_form, **kwargs):
        context = super(AccountCreateFormView, self).get_context_data(**kwargs)
        context['account_create_form'] = account_create_form
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('index_url'))

        return render_to_response(self.template_name, self.get_context_data(),
                                  context_instance=RequestContext(request))

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('index_url'))

        account_create_form = AccountCreateForm(request.POST)
        if account_create_form.is_valid():
            if account_create_form.cleaned_data['account_type'] == AccountCreateForm.ACCOUNT_TYPE_STAFF:
                user = Teacher()
                user.is_staff = True
            else:
                user = Student()
                user.is_staff = False
                user.student_no = account_create_form.cleaned_data.get('student_no')

            user.username = account_create_form.cleaned_data.get('username')
            user.email = account_create_form.cleaned_data.get('email')
            user.set_password(account_create_form.cleaned_data.get('password'))

            try:
                user.save()
            except IntegrityError:
                account_create_form.add_error('username', 'User with given username already exists.')
                return render_to_response(self.template_name, self.create_context_data(account_create_form),
                                          context_instance=RequestContext(request))

            messages.add_message(request, messages.SUCCESS, 'Account created.')
            return HttpResponseRedirect(reverse('account_login_url'))

        return render_to_response(self.template_name, self.create_context_data(account_create_form),
                                  context_instance=RequestContext(request))


class LoginFormView(FormView):
    template_name = 'account/login.html'
    form_class = LoginForm

    def get_context_data(self, **kwargs):
        context = super(LoginFormView, self).get_context_data(**kwargs)
        context['login_form'] = LoginForm()
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('index_url'))

        return render_to_response(self.template_name, self.get_context_data(),
                                  context_instance=RequestContext(request))

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('index_url'))

        if self.request.POST:
            username = self.request.POST['username']
            password = self.request.POST['password']

            user = auth_authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)

                if self.request.GET.get('next'):
                    return HttpResponseRedirect(self.request.GET.get('next'))

                return HttpResponseRedirect(reverse('index_url'))

        messages.add_message(request, messages.ERROR, 'Username or password is incorrect. Try again.')
        return render_to_response(self.template_name, self.get_context_data(),
                                  context_instance=RequestContext(request))


@method_decorator(login_required, name='dispatch')
class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        return render_to_response(self.template_name, self.get_context_data(),
                                  context_instance=RequestContext(request))


@login_required
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('account_login_url'))


@method_decorator(login_required, name='dispatch')
class TeamListView(TemplateView):
    template_name = 'team/list.html'

    def get_context_data(self, teams, **kwargs):
        context = super(TeamListView, self).get_context_data(**kwargs)
        context['teams'] = teams
        return context

    def get(self, request, *args, **kwargs):
        teams = Team.objects.all()
        return render_to_response(self.template_name, self.get_context_data(teams),
                                  context_instance=RequestContext(request))


@method_decorator(login_required, name='dispatch')
class TeamCreateFormView(FormView):
    template_name = 'team/create.html'
    form_class = TeamCreateForm

    def get_context_data(self, **kwargs):
        return self.create_context_data(TeamCreateForm(self.request.POST)
                                        if self.request.method == "POST" else TeamCreateForm())

    def create_context_data(self, team_create_form, **kwargs):
        context = super(TeamCreateFormView, self).get_context_data(**kwargs)
        context['team_create_form'] = team_create_form
        return context

    def get(self, request, *args, **kwargs):
        return render_to_response(self.template_name, self.get_context_data(),
                                  context_instance=RequestContext(request))

    def post(self, request, *args, **kwargs):
        team_create_form = TeamCreateForm(request.POST)
        if team_create_form.is_valid():
            try:
                user_create_team(request.user, team_create_form.cleaned_data.get('name'))
            except MustBeStudent:
                messages.add_message(request, messages.ERROR, 'Only students are allowed to create a team.')
                return HttpResponseRedirect(reverse('teams_list_url'))

            except UserAlreadyInTeam:
                messages.add_message(request, messages.ERROR, 'You already have a team. Quit your team first.')
                return HttpResponseRedirect(reverse('teams_list_url'))

            messages.add_message(request, messages.SUCCESS, 'Team created.')
            return HttpResponseRedirect(reverse('teams_list_url'))

        return render_to_response(self.template_name, self.create_context_data(team_create_form),
                                  context_instance=RequestContext(request))


@require_http_methods(["POST"])
@login_required
def team_join(request):
    try:
        team = Team.objects.get(id=request.POST.get('team_id'))
    except (KeyError, Team.DoesNotExist):
        messages.add_message(request, messages.ERROR, 'Invalid team.')
        return HttpResponseRedirect(reverse('teams_list_url'))

    try:
        user_join_team(request.user, team)
    except MustBeStudent:
        messages.add_message(request, messages.ERROR, 'Only students are allowed to join a team.')
        return HttpResponseRedirect(reverse('teams_list_url'))
    except UserAlreadyInTeam:
        messages.add_message(request, messages.ERROR, 'You already have a team. Quit your team first.')
        return HttpResponseRedirect(reverse('teams_list_url'))

    return HttpResponseRedirect(reverse('teams_list_url'))


@login_required
def team_leave(request):
    try:
        user_team_leave(request.user)
    except MustBeStudent:
        messages.add_message(request, messages.ERROR, 'You must be a student to quit a team.')
        return HttpResponseRedirect(reverse('teams_list_url'))
    except UserNotInTeam:
        messages.add_message(request, messages.ERROR, 'You must be in a team in order to quit it.')
        return HttpResponseRedirect(reverse('teams_list_url'))

    messages.add_message(request, messages.INFO, 'You left the team.')
    return HttpResponseRedirect(reverse('teams_list_url'))


@method_decorator(login_required, name='dispatch')
class ProjectListView(TemplateView):
    template_name = 'project/list.html'

    def get_context_data(self, projects, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        context['projects'] = projects
        return context

    def get(self, request, *args, **kwargs):
        projects = Project.objects.all()
        return render_to_response(self.template_name, self.get_context_data(projects),
                                  context_instance=RequestContext(request))


@method_decorator(login_required, name='dispatch')
class ProjectCreateFormView(FormView):
    template_name = 'project/create.html'
    form_class = ProjectCreateForm

    def get_context_data(self, **kwargs):
        return self.create_context_data(ProjectCreateForm(self.request.POST)
                                        if self.request.method == "POST" else ProjectCreateForm())

    def create_context_data(self, project_create_form, **kwargs):
        context = super(ProjectCreateFormView, self).get_context_data(**kwargs)
        context['project_create_form'] = project_create_form
        return context

    def get(self, request, *args, **kwargs):
        return render_to_response(self.template_name, self.get_context_data(),
                                  context_instance=RequestContext(request))

    def post(self, request, *args, **kwargs):
        project_create_form = ProjectCreateForm(request.POST)
        if project_create_form.is_valid():
            try:
                user_create_project(request.user, project_create_form.cleaned_data.get('name'),
                                    project_create_form.cleaned_data.get('description'))
            except MustBeTeacher:
                messages.add_message(request, messages.ERROR, 'Only teachers are allowed to create projects.')
                return HttpResponseRedirect(reverse('projects_list_url'))

            messages.add_message(request, messages.SUCCESS, 'Project created.')
            return HttpResponseRedirect(reverse('projects_list_url'))

        return render_to_response(self.template_name, self.create_context_data(project_create_form),
                                  context_instance=RequestContext(request))


@require_http_methods(["POST"])
@login_required
def project_join(request):
    try:
        project = Project.objects.get(pk=request.POST.get('project_id'))
    except (KeyError, Project.DoesNotExist):
        messages.add_message(request, messages.ERROR, 'Invalid project.')
        return HttpResponseRedirect(reverse('projects_list_url'))

    try:
        user_team_join_project(request.user, project)
    except MustBeStudent:
        messages.add_message(request, messages.ERROR, 'Only students are allowed to assign their team to a project.')
        return HttpResponseRedirect(reverse('projects_list_url'))
    except UserNotInTeam:
        messages.add_message(request, messages.ERROR, 'You have no team. Join or create your own team first.')
        return HttpResponseRedirect(reverse('projects_list_url'))
    except ProjectHasAssignedTeam:
        messages.add_message(request, messages.ERROR, 'This project has already an assigned team.')
        return HttpResponseRedirect(reverse('projects_list_url'))

    return HttpResponseRedirect(reverse('projects_list_url'))


@require_http_methods(["POST"])
@login_required
def project_delete(request):
    try:
        project = Project.objects.get(pk=request.POST.get('project_id'))
    except (KeyError, Project.DoesNotExist):
        messages.add_message(request, messages.ERROR, 'Invalid project.')
        return HttpResponseRedirect(reverse('projects_list_url'))

    try:
        user_delete_project(request.user, project)
    except MustBeTeacher:
        messages.add_message(request, messages.ERROR, 'Only teachers are allowed to delete projects.')
        return HttpResponseRedirect(reverse('projects_list_url'))
    except ProjectHasAssignedTeam:
        messages.add_message(request, messages.ERROR, 'You cannot delete a project that has an assigned team.')
        return HttpResponseRedirect(reverse('projects_list_url'))

    messages.add_message(request, messages.INFO, 'Project deleted.')
    return HttpResponseRedirect(reverse('projects_list_url'))

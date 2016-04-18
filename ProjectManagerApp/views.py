from django.contrib.auth import authenticate as auth_authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import FormView
from django.views.generic import TemplateView

from ProjectManagerApp.forms import LoginForm, AccountCreateForm, ProjectCreateForm, TeamCreateForm
from ProjectManagerApp.models import Project, Teacher, Student, Team


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
            return HttpResponseRedirect('/index')

        return render_to_response(self.template_name, self.get_context_data(),
                                  context_instance=RequestContext(request))

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/index')

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

            return HttpResponseRedirect('/account/login')

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
            return HttpResponseRedirect('/index')

        return render_to_response(self.template_name, self.get_context_data(),
                                  context_instance=RequestContext(request))

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/index')

        if self.request.POST:
            username = self.request.POST['username']
            password = self.request.POST['password']

            user = auth_authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return HttpResponseRedirect('/index')

        messages.add_message(request, messages.ERROR, 'Username or password is incorrect. Try again.')
        return render_to_response(self.template_name, self.get_context_data(),
                                  context_instance=RequestContext(request))


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return render_to_response(self.template_name, self.get_context_data(),
                                      context_instance=RequestContext(request))

        return HttpResponseRedirect('/account/login')


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/account/login')


class TeamListView(TemplateView):
    template_name = 'team/list.html'

    def get_context_data(self, teams, **kwargs):
        context = super(TeamListView, self).get_context_data(**kwargs)
        context['teams'] = teams
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            teams = Team.objects.all()
            return render_to_response(self.template_name, self.get_context_data(teams),
                                      context_instance=RequestContext(request))

        return HttpResponseRedirect('/account/login')


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
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/account/login')

        if not isinstance(request.user, Student):
            messages.add_message(request, messages.ERROR, 'Access denied. Teachers cannot create a new team.')
            return HttpResponseRedirect('/index')

        return render_to_response(self.template_name, self.get_context_data(),
                                  context_instance=RequestContext(request))

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/account/login')

        if not isinstance(request.user, Student):
            messages.add_message(request, messages.ERROR, 'Access denied. Teachers cannot create a new team.')
            return HttpResponseRedirect('/index')

        team_create_form = TeamCreateForm(request.POST)
        if team_create_form.is_valid():
            team = Team()
            team.name = team_create_form.cleaned_data.get('name')
            team.first_teammate = request.user
            team.save()

            return HttpResponseRedirect('/teams')

        return render_to_response(self.template_name, self.create_context_data(team_create_form),
                                  context_instance=RequestContext(request))


def team_join(request):
    team = Team.objects.get(id=request.POST.get('team_id'))
    if team.first_teammate is None:
        team.first_teammate = request.user
    elif team.second_teammate is None:
        team.second_teammate = request.user
    team.save(force_update=True)
    return HttpResponseRedirect('/teams')


def team_leave(request):
    team = Team.objects.get(id=request.POST.get('team_id'))
    if team.first_teammate == request.user:
        team.first_teammate = None
    elif team.second_teammate == request.user:
        team.second_teammate = None
    team.save(force_update=True)

    if team.first_teammate is None and team.second_teammate is None:
        # TODO exception checking
        team.delete()
        messages.add_message(request, messages.INFO, 'Team was deleted.')
    return HttpResponseRedirect('/teams')


class ProjectListView(TemplateView):
    template_name = 'project/list.html'

    def get_context_data(self, projects, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        context['projects'] = projects
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            projects = Project.objects.all()
            return render_to_response(self.template_name, self.get_context_data(projects),
                                      context_instance=RequestContext(request))

        return HttpResponseRedirect('/account/login')


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
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/account/login')

        if not isinstance(request.user, Teacher):
            messages.add_message(request, messages.ERROR, 'Access denied. Students cannot create a new project.')
            return HttpResponseRedirect('/index')

        return render_to_response(self.template_name, self.get_context_data(),
                                  context_instance=RequestContext(request))

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/account/login')

        if not isinstance(request.user, Teacher):
            messages.add_message(request, messages.ERROR, 'Access denied. Students cannot create a new project.')
            return HttpResponseRedirect('/index')

        project_create_form = ProjectCreateForm(request.POST)
        if project_create_form.is_valid():
            project = Project()
            project.name = project_create_form.cleaned_data.get('name')
            project.description = project_create_form.cleaned_data.get('description')
            project.status = Project.PROJECT_STATUS_OPEN
            project.author = request.user
            project.save()

            return HttpResponseRedirect('/projects')

        return render_to_response(self.template_name, self.create_context_data(project_create_form),
                                  context_instance=RequestContext(request))


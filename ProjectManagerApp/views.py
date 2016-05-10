from django.contrib.auth import authenticate as auth_authenticate, login as auth_login, logout as auth_logout, \
    update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import FormView
from django.views.generic import TemplateView

from ProjectManagerApp.exceptions import MustBeStudent, UserAlreadyInTeam, UserNotInTeam, MustBeTeacher, \
    ProjectHasAssignedTeam, UserWithGivenUsernameAlreadyExists, StudentWithGivenStudentNoAlreadyExists, \
    TeamAlreadyInProjectQueue, TeamNotInProjectQueue, UserWithGivenEmailAlreadyExists, InvalidPassword
from ProjectManagerApp.forms import LoginForm, AccountCreateForm, ProjectCreateForm, TeamCreateForm, \
    AccountChangeEmailForm, AccountChangePasswordForm
from ProjectManagerApp.models import Project, Team
from ProjectManagerApp.services import user_join_team, user_create_team, user_team_leave, user_delete_project, \
    user_create_project, user_team_join_project, account_create_teacher, account_create_student, \
    user_team_leave_project, user_change_email, user_change_password


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
            return redirect(reverse('index_url'))

        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse('index_url'))

        account_create_form = AccountCreateForm(request.POST)
        if account_create_form.is_valid():
            try:
                if account_create_form.cleaned_data['account_type'] == AccountCreateForm.ACCOUNT_TYPE_STAFF:
                    account_create_teacher(account_create_form.cleaned_data.get('username'),
                                           account_create_form.cleaned_data.get('email'),
                                           account_create_form.cleaned_data.get('password'))
                else:
                    account_create_student(account_create_form.cleaned_data.get('student_no'),
                                           account_create_form.cleaned_data.get('username'),
                                           account_create_form.cleaned_data.get('email'),
                                           account_create_form.cleaned_data.get('password'))
            except UserWithGivenUsernameAlreadyExists:
                account_create_form.add_error('username', 'User with given username already exists.')
                return render(request, self.template_name, self.create_context_data(account_create_form))
            except UserWithGivenEmailAlreadyExists:
                account_create_form.add_error('email', 'User with given email already exists.')
                return render(request, self.template_name, self.create_context_data(account_create_form))
            except StudentWithGivenStudentNoAlreadyExists:
                account_create_form.add_error('student_no', 'Student with given student no already exists.')
                return render(request, self.template_name, self.create_context_data(account_create_form))

            messages.add_message(request, messages.SUCCESS, 'Account created.')
            return redirect(reverse('account_login_url'))

        return render(request, self.template_name, self.create_context_data(account_create_form))


class LoginFormView(FormView):
    template_name = 'account/login.html'
    form_class = LoginForm

    def get_context_data(self, **kwargs):
        context = super(LoginFormView, self).get_context_data(**kwargs)
        context['login_form'] = LoginForm()
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse('index_url'))

        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse('index_url'))

        if self.request.POST:
            username = self.request.POST['username']
            password = self.request.POST['password']

            user = auth_authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)

                if self.request.GET.get('next'):
                    return redirect(self.request.GET.get('next'))

                return redirect(reverse('index_url'))

        messages.add_message(request, messages.ERROR, 'Username or password is incorrect. Try again.')
        return render(request, self.template_name, self.get_context_data())


@method_decorator(login_required, name='dispatch')
class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())


def logout(request):
    auth_logout(request)
    return redirect(reverse('account_login_url'))


@method_decorator(login_required, name='dispatch')
class AccountDetailsView(TemplateView):
    template_name = 'account/details.html'

    def get_context_data(self, **kwargs):
        context = super(AccountDetailsView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())


@method_decorator(login_required, name='dispatch')
class AccountChangeEmailFormView(FormView):
    template_name = 'account/changeEmail.html'
    form_class = AccountChangeEmailForm

    def get_context_data(self, **kwargs):
        return self.create_context_data(AccountChangeEmailForm(self.request.POST)
                                        if self.request.method == "POST" else AccountChangeEmailForm())

    def create_context_data(self, account_change_email_form, **kwargs):
        context = super(AccountChangeEmailFormView, self).get_context_data(**kwargs)
        context['account_change_email_form'] = account_change_email_form
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        account_change_email_form = AccountChangeEmailForm(request.POST)
        if account_change_email_form.is_valid():
            try:
                user_change_email(request.user, account_change_email_form.cleaned_data.get('new_email'))
            except UserWithGivenEmailAlreadyExists:
                messages.add_message(request, messages.ERROR, 'User with given email already exists.')
                return render(request, self.template_name, self.get_context_data())

            messages.add_message(request, messages.SUCCESS, 'Email changed.')
            return render(request, self.template_name, self.get_context_data())

        return render(request, self.template_name, self.create_context_data(account_change_email_form))


@method_decorator(login_required, name='dispatch')
class AccountChangePasswordFormView(FormView):
    template_name = 'account/changePassword.html'
    form_class = AccountChangePasswordForm

    def get_context_data(self, **kwargs):
        return self.create_context_data(AccountChangePasswordForm(self.request.POST)
                                        if self.request.method == "POST" else AccountChangePasswordForm())

    def create_context_data(self, account_change_password_form, **kwargs):
        context = super(AccountChangePasswordFormView, self).get_context_data(**kwargs)
        context['account_change_password_form'] = account_change_password_form
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        account_change_password_form = AccountChangePasswordForm(request.POST)
        if account_change_password_form.is_valid():
            try:
                user_change_password(request.user, account_change_password_form.cleaned_data.get('current_password'),
                                     account_change_password_form.cleaned_data.get('new_password'))
                update_session_auth_hash(request, request.user)
            except InvalidPassword:
                messages.add_message(request, messages.ERROR, 'Invalid current password.')
                return render(request, self.template_name, self.get_context_data())

            messages.add_message(request, messages.SUCCESS, 'Password changed.')
            return render(request, self.template_name, self.get_context_data())

        return render(request, self.template_name, self.create_context_data(account_change_password_form))


@method_decorator(login_required, name='dispatch')
class TeamListView(TemplateView):
    template_name = 'team/list.html'

    def get_context_data(self, teams, **kwargs):
        context = super(TeamListView, self).get_context_data(**kwargs)
        context['teams'] = teams
        return context

    def get(self, request, *args, **kwargs):
        teams = Team.objects.all()
        return render(request, self.template_name, self.get_context_data(teams))


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
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        team_create_form = TeamCreateForm(request.POST)
        if team_create_form.is_valid():
            try:
                user_create_team(request.user, team_create_form.cleaned_data.get('name'))
            except MustBeStudent:
                messages.add_message(request, messages.ERROR, 'Only students are allowed to create a team.')
                return redirect(reverse('teams_list_url'))

            except UserAlreadyInTeam:
                messages.add_message(request, messages.ERROR, 'You already have a team. Quit your team first.')
                return redirect(reverse('teams_list_url'))

            messages.add_message(request, messages.SUCCESS, 'Team created.')
            return redirect(reverse('teams_list_url'))

        return render(request, self.template_name, self.create_context_data(team_create_form))


@require_http_methods(["POST"])
@login_required
def team_join(request):
    try:
        team = Team.objects.get(id=request.POST.get('team_id'))
    except (KeyError, Team.DoesNotExist):
        messages.add_message(request, messages.ERROR, 'Invalid team.')
        return redirect(reverse('teams_list_url'))

    try:
        user_join_team(request.user, team)
    except MustBeStudent:
        messages.add_message(request, messages.ERROR, 'Only students are allowed to join a team.')
        return redirect(reverse('teams_list_url'))
    except UserAlreadyInTeam:
        messages.add_message(request, messages.ERROR, 'You already have a team. Quit your team first.')
        return redirect(reverse('teams_list_url'))

    return redirect(reverse('teams_list_url'))


@method_decorator(login_required, name='dispatch')
class TeamDetailsView(TemplateView):
    template_name = 'team/details.html'

    def get(self, request, *args, **kwargs):
        try:
            team = Team.objects.get(pk=request.GET.get('id'))
        except (KeyError, Team.DoesNotExist):
            messages.add_message(request, messages.ERROR, 'Invalid team.')
            return redirect(reverse('teams_list_url'))

        return render(request, self.template_name, {'team': team})


@login_required
def team_leave(request):
    try:
        user_team_leave(request.user)
    except MustBeStudent:
        messages.add_message(request, messages.ERROR, 'You must be a student to quit a team.')
        return redirect(reverse('teams_list_url'))
    except UserNotInTeam:
        messages.add_message(request, messages.ERROR, 'You must be in a team in order to quit it.')
        return redirect(reverse('teams_list_url'))

    messages.add_message(request, messages.INFO, 'You left the team.')
    return redirect(reverse('teams_list_url'))


@method_decorator(login_required, name='dispatch')
class ProjectListView(TemplateView):
    template_name = 'project/list.html'

    def get_context_data(self, projects, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        context['projects'] = projects
        return context

    def get(self, request, *args, **kwargs):
        projects = Project.objects.all()
        return render(request, self.template_name, self.get_context_data(projects))


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
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        project_create_form = ProjectCreateForm(request.POST)
        if project_create_form.is_valid():
            try:
                user_create_project(request.user, project_create_form.cleaned_data.get('name'),
                                    project_create_form.cleaned_data.get('description'))
            except MustBeTeacher:
                messages.add_message(request, messages.ERROR, 'Only teachers are allowed to create projects.')
                return redirect(reverse('projects_list_url'))

            messages.add_message(request, messages.SUCCESS, 'Project created.')
            return redirect(reverse('projects_list_url'))

        return render(request, self.template_name, self.create_context_data(project_create_form))


@require_http_methods(["POST"])
@login_required
def project_join(request):
    try:
        project = Project.objects.get(pk=request.POST.get('project_id'))
    except (KeyError, Project.DoesNotExist):
        messages.add_message(request, messages.ERROR, 'Invalid project.')
        return redirect(reverse('projects_list_url'))

    try:
        user_team_join_project(request.user, project)
    except MustBeStudent:
        messages.add_message(request, messages.ERROR, 'Only students are allowed to assign their team to a project.')
        return redirect(reverse('projects_list_url'))
    except UserNotInTeam:
        messages.add_message(request, messages.ERROR, 'You have no team. Join or create your own team first.')
        return redirect(reverse('projects_list_url'))
    except TeamAlreadyInProjectQueue:
        messages.add_message(request, messages.ERROR, 'Your team is already in the project queue.')
        return redirect(reverse('projects_list_url'))
    except ProjectHasAssignedTeam:
        messages.add_message(request, messages.ERROR, 'This project has already an assigned team.')
        return redirect(reverse('projects_list_url'))

    return redirect(reverse('projects_list_url'))


@require_http_methods(["POST"])
@login_required
def project_leave(request):
    try:
        project = Project.objects.get(pk=request.POST.get('project_id'))
    except (KeyError, Project.DoesNotExist):
        messages.add_message(request, messages.ERROR, 'Invalid project.')
        return redirect(reverse('projects_list_url'))

    try:
        user_team_leave_project(request.user, project)
    except MustBeStudent:
        messages.add_message(request, messages.ERROR, 'Only students are allowed to assign their team to a project.')
        return redirect(reverse('projects_list_url'))
    except UserNotInTeam:
        messages.add_message(request, messages.ERROR, 'You have no team. Join or create your own team first.')
        return redirect(reverse('projects_list_url'))
    except TeamNotInProjectQueue:
        messages.add_message(request, messages.ERROR, 'Your team is not in the project queue.')
        return redirect(reverse('projects_list_url'))
    except ProjectHasAssignedTeam:
        messages.add_message(request, messages.ERROR, 'This project has already an assigned team.')
        return redirect(reverse('projects_list_url'))

    return redirect(reverse('projects_list_url'))


@method_decorator(login_required, name='dispatch')
class ProjectDetailsView(TemplateView):
    template_name = 'project/details.html'

    def get(self, request, *args, **kwargs):
        try:
            project = Project.objects.get(pk=request.GET.get('id'))
        except (KeyError, Project.DoesNotExist):
            messages.add_message(request, messages.ERROR, 'Invalid project.')
            return redirect(reverse('projects_list_url'))

        return render(request, self.template_name, {'project': project})


@require_http_methods(["POST"])
@login_required
def project_delete(request):
    try:
        project = Project.objects.get(pk=request.POST.get('project_id'))
    except (KeyError, Project.DoesNotExist):
        messages.add_message(request, messages.ERROR, 'Invalid project.')
        return redirect(reverse('projects_list_url'))

    try:
        user_delete_project(request.user, project)
    except MustBeTeacher:
        messages.add_message(request, messages.ERROR, 'Only teachers are allowed to delete projects.')
        return redirect(reverse('projects_list_url'))
    except ProjectHasAssignedTeam:
        messages.add_message(request, messages.ERROR, 'You cannot delete a project that has an assigned team.')
        return redirect(reverse('projects_list_url'))

    messages.add_message(request, messages.INFO, 'Project deleted.')
    return redirect(reverse('projects_list_url'))

from django.contrib.auth import authenticate as auth_authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import FormView

from ProjectManagerApp.forms import LoginForm, AccountCreateForm, ProjectCreateForm
from ProjectManagerApp.models import Project

class AccountCreateFormView(FormView):
    template_name = 'account/create.html'
    form_class = AccountCreateForm

    def get_context_data(self, **kwargs):
        return self.create_context_data(AccountCreateForm(self.request.POST) if self.request.method == "POST" else AccountCreateForm())

    def create_context_data(self, account_create_form, **kwargs):
        context = super(AccountCreateFormView, self).get_context_data(**kwargs)
        context['account_create_form'] = account_create_form
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/index')

        return render_to_response(self.template_name, self.get_context_data(), context_instance=RequestContext(request))

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/index')

        account_create_form = AccountCreateForm(request.POST)
        if account_create_form.is_valid():
            user = User()
            user.username = account_create_form.cleaned_data.get('username')
            user.email = account_create_form.cleaned_data.get('email')
            user.set_password(account_create_form.cleaned_data.get('password'))
            user.is_staff = True if account_create_form.cleaned_data['account_type'] == AccountCreateForm.ACCOUNT_TYPE_STAFF else False

            try:
                user.save()
            except IntegrityError:
                account_create_form.add_error('username', 'User with given username already exists.')
                return render_to_response(self.template_name, self.create_context_data(account_create_form), context_instance=RequestContext(request))

            return HttpResponseRedirect('/account/login')

        return render_to_response(self.template_name, self.create_context_data(account_create_form), context_instance=RequestContext(request))


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

        return render_to_response(self.template_name, self.get_context_data(), context_instance=RequestContext(request))

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/index')

        username = password = ''
        if self.request.POST:
            username = self.request.POST['username']
            password = self.request.POST['password']

            user = auth_authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return HttpResponseRedirect('/index')

        return render_to_response(self.template_name, self.get_context_data(), context_instance=RequestContext(request))


def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/index')

    return HttpResponseRedirect('/account/login')


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/account/login')


class ProjectCreateFormView(FormView):
    template_name = 'project/create.html'
    form_class = ProjectCreateForm

    def get_context_data(self, **kwargs):
        return self.create_context_data(ProjectCreateForm(self.request.POST) if self.request.method == "POST" else ProjectCreateForm())

    def create_context_data(self, project_create_form, **kwargs):
        context = super(ProjectCreateFormView, self).get_context_data(**kwargs)
        context['project_create_form'] = project_create_form
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/account/login')

        return render_to_response(self.template_name, self.get_context_data(), context_instance=RequestContext(request))

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/account/login')

        project_create_form = ProjectCreateForm(request.POST)
        if project_create_form.is_valid():
            project = Project()
            project.name = project_create_form.cleaned_data.get('name')
            project.description = project_create_form.cleaned_data.get('description')
            project.status = 'O'

            try:
                project.save()
            except IntegrityError:
                project_create_form.add_error('name', 'Project with given name already exists.')
                return render_to_response(self.template_name, self.create_context_data(project_create_form), context_instance=RequestContext(request))

            return HttpResponseRedirect('/projects/create')

        return render_to_response(self.template_name, self.create_context_data(project_create_form), context_instance=RequestContext(request))


from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as logoutFunc
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import FormView

from ProjectManagerApp.forms import LoginForm


class LoginFormView(FormView):
    template_name = 'account/login.html'
    form_class = LoginForm

    def get_context_data(self, **kwargs):
        context = super(LoginFormView, self).get_context_data(**kwargs)
        context['login_form'] = LoginForm()
        return context

    def get(self, request, *args, **kwargs):
        return render_to_response(self.template_name, self.get_context_data(), context_instance=RequestContext(request))

    def post(self, request, *args, **kwargs):
        username = password = ''
        if self.request.POST:
            username = self.request.POST['username']
            password = self.request.POST['password']

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/index')

        return render_to_response(self.template_name, self.get_context_data(), context_instance=RequestContext(request))


def logout(request):
    logoutFunc(request)
    return HttpResponseRedirect('/account/login')

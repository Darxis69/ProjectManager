from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import FormView

from ProjectManagerApp.forms import LoginForm


class LoginFormView(FormView):
    template_name = 'login.html'
    form_class = LoginForm

    def get_context_data(self, **kwargs):
        context = super(LoginFormView, self).get_context_data(**kwargs)
        context['form'] = LoginForm()
        return context

    def get(self, request, *args, **kwargs):
        return render_to_response(self.template_name, self.get_context_data(), context_instance=RequestContext(request))

    def post(self, request, *args, **kwargs):
        username = password = ''
        if self.request.POST:
            username = self.request.POST['username']
            password = self.request.POST['password']

            if username == 'admin' and password == 'admin':
                return HttpResponseRedirect('/index')

        return render_to_response(self.template_name, self.get_context_data(), context_instance=RequestContext(request))


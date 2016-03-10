from django import forms
from django.forms import PasswordInput


class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=PasswordInput())

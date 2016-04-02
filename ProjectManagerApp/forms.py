from django import forms
from django.core.exceptions import ValidationError
from django.forms import PasswordInput


class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=PasswordInput())


class AccountCreateForm(forms.Form):
    ACCOUNT_TYPE_STUDENT = '1'
    ACCOUNT_TYPE_STUDENT_LABEL = 'Student'
    ACCOUNT_TYPE_STAFF = '2'
    ACCOUNT_TYPE_STAFF_LABEL = 'Staff'

    ACCOUNT_TYPES = (
        (ACCOUNT_TYPE_STUDENT, ACCOUNT_TYPE_STUDENT_LABEL),
        (ACCOUNT_TYPE_STAFF, ACCOUNT_TYPE_STAFF_LABEL),
    )

    username = forms.CharField(label='Username')
    email = forms.EmailField(label="Email")
    password = forms.CharField(label='Password', widget=PasswordInput())
    password_repeat = forms.CharField(label='Password repeat', widget=PasswordInput())
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPES)

    def clean(self):
        cleaned_password = self.cleaned_data.get('password')
        cleaned_password_repeat = self.cleaned_data.get('password_repeat')

        if cleaned_password != cleaned_password_repeat:
            raise ValidationError("Passwords don't match.", code='not_match')

        return self.cleaned_data

class ProjectCreateForm(forms.Form):
    name = forms.CharField(label='Project name')
    description = forms.CharField(label="Description")

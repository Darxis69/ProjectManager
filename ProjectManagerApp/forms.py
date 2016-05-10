from django import forms
from django.forms import PasswordInput


class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=PasswordInput())


class AccountChangeEmailForm(forms.Form):
    new_email = forms.EmailField(label='New email')


class AccountChangePasswordForm(forms.Form):
    current_password = forms.CharField(label='Current password', widget=PasswordInput())
    new_password = forms.CharField(label='New password', widget=PasswordInput())
    new_password_repeat = forms.CharField(label='New password repeat', widget=PasswordInput())

    def clean(self):
        cleaned_new_password = self.cleaned_data.get('new_password')
        cleaned_new_password_repeat = self.cleaned_data.get('new_password_repeat')

        if cleaned_new_password != cleaned_new_password_repeat:
            self.add_error('new_password_repeat', "Passwords don't match.")

        return self.cleaned_data


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
    student_no = forms.CharField(label='Student No.', required=False)

    def clean(self):
        cleaned_password = self.cleaned_data.get('password')
        cleaned_password_repeat = self.cleaned_data.get('password_repeat')

        if cleaned_password != cleaned_password_repeat:
            self.add_error('password_repeat', "Passwords don't match.")

        cleaned_student_no = self.cleaned_data.get('student_no')
        cleaned_account_type = self.cleaned_data.get('account_type')

        if cleaned_account_type == self.ACCOUNT_TYPE_STUDENT:
            if cleaned_student_no == '':
                self.add_error('student_no', "Student No. required.")
            if not cleaned_student_no.isdigit():
                self.add_error('student_no', "Student No. must be a number")

        return self.cleaned_data


class ProjectCreateForm(forms.Form):
    name = forms.CharField(label='Project name')
    description = forms.CharField(label="Description", widget=forms.Textarea)


class TeamCreateForm(forms.Form):
    name = forms.CharField(label='Team name')

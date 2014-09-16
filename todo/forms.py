from django import forms

from todo.models import User

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=40)
    password = forms.CharField(label='Password', max_length=40, widget=forms.PasswordInput)


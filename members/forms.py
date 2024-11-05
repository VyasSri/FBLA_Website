from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    is_staff = forms.ChoiceField(
        choices=[(False, 'Student'), (True, 'Company')],
        label='Select your role',
        widget=forms.Select
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "is_staff"]

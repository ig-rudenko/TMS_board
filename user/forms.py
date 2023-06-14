from django.contrib.auth.forms import UserCreationForm
from django import forms
from captcha.fields import CaptchaField

from .models import User


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

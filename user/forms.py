from typing import Any
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model

from django.contrib.auth import authenticate, login


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        email, password = cleaned_data.get('email',False), cleaned_data.get('password',False)
        if email and password:
            user = authenticate(
                self.request,
                username=cleaned_data["email"],
                password=cleaned_data["password"],
            )
            if user is None:
                raise forms.ValidationError({"email": ["Invalid email or password"]})
            login(self.request, user)
        return cleaned_data


class UserCreationForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = ["name", "email", "password", "confirm_password"]

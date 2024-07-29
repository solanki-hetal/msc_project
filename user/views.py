from typing import Any
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from user.forms import UserCreationForm, UserLoginForm

# Create your views here.


class LoginView(FormView):
    template_name = "login.html"
    form_class = UserLoginForm
    success_url = reverse_lazy("home")

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)

        return response


class RegisterView(FormView):
    template_name = "register.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

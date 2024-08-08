from typing import Any
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from user.forms import UserCreationForm, UserLoginForm
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import logout

# Create your views here.


def logout_user(request):
    logout(request)
    return redirect("tracker:home")


class LoginView(FormView, SuccessMessageMixin):
    template_name = "login.html"
    form_class = UserLoginForm
    success_url = reverse_lazy("tracker:home")
    success_message = "You are successfully logged in"
    
    def get_success_url(self) -> str:
        if "next" in self.request.GET:
            return self.request.GET["next"]
        return super().get_success_url()

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs


class RegisterView(FormView, SuccessMessageMixin):
    template_name = "register.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("user:login")
    success_message = "You are successfully registered. Check you email for verification."

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

from typing import Any
from django.views.generic import ListView, CreateView, UpdateView
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from tracker import forms, models

# Create your views here.


@login_required
def home(request):
    return render(request, "home.html")


class TokenListView(ListView):
    model = models.GitToken
    template_name = "token_list.html"
    context_object_name = "tokens"

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class TokenCreateView(CreateView):
    form_class = forms.TokenForm
    template_name = "token_form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TokenEditView(UpdateView):
    form_class = forms.TokenForm
    template_name = "token_form.html"
    model = models.GitToken

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.get_object()
        return kwargs

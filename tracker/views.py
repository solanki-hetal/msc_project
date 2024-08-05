from typing import Any

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import CreateView, ListView, UpdateView

from core.views import BaseCreateView, BaseUpdateView
from tracker import forms, models
from django.contrib import messages

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


class TokenCreateView(BaseCreateView):
    form_class = forms.TokenForm
    model = models.GitToken

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TokenEditView(BaseUpdateView):
    form_class = forms.TokenForm
    model = models.GitToken

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

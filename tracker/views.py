from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.views import BaseCreateView, BaseListView, BaseUpdateView
from tracker import forms, models


@login_required
def home(request):
    return render(request, "home.html")


class TokenListView(BaseListView):
    model = models.GitToken
    create_button_label = "Create Token"
    list_display = ["label", "service", "is_active"]

    def get_queryset(self):
        if self.request.user.has_perm("can_view_all_git_tokens"):
            return self.model.objects.all()
        return self.model.objects.filter(user=self.request.user)


class RepositoryListView(BaseListView):
    model = models.Repository
    list_display = ["name", "owner", "private", "language", "last_synced_at"]
    can_create = False
    can_edit = False

    def get_queryset(self):
        if self.request.user.has_perm("can_view_all_repositories"):
            return self.model.objects.all()
        return self.model.objects.filter(users=self.request.user)


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

from typing import Any

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, F, Func, Max, Min, Sum
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.utils.timezone import now, timedelta
from django.views.generic import DetailView
from django.db.models.functions import ExtractHour

from core.views import BaseCreateView, BaseListView, BaseUpdateView, ListAction
from tracker import forms, models

from .models import Commit, Repository


@login_required
def home(request):
    return render(request, "home.html")


class TokenCreateView(LoginRequiredMixin, BaseCreateView):
    form_class = forms.TokenForm
    model = models.GitToken

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TokenEditView(LoginRequiredMixin, BaseUpdateView):
    form_class = forms.TokenForm
    model = models.GitToken

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class TokenListView(LoginRequiredMixin, BaseListView):
    model = models.GitToken
    create_button_label = "Create Token"
    list_display = ["label", "service", "is_active"]

    def get_queryset(self):
        if self.request.user.has_perm("can_view_all_git_tokens"):
            return self.model.objects.all()
        return self.model.objects.filter(user=self.request.user)


class RepositoryListView(LoginRequiredMixin, BaseListView):
    model = models.Repository
    list_display = ["name", "owner", "private", "language", "last_synced_at"]
    can_create = False
    can_edit = False
    actions = [
        ListAction(
            "Commits",
            "bi-eye",
            models.RepositoryAction.COMMITS,
            tooltip="View Commits",
        ),
        ListAction(
            "Analysis",
            "bi-graph-up-arrow",
            models.RepositoryAction.ANALYSIS,
            tooltip="View Analysis",
        ),
    ]

    def get_queryset(self):
        if self.request.user.has_perm("can_view_all_repositories"):
            return self.model.objects.all()
        return self.model.objects.filter(users=self.request.user)


class RepositoryStatsView(DetailView):
    model = Repository
    template_name = "repository_stats.html"
    context_object_name = "repository"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        repository = self.object

        commit_frequency = (
            Commit.objects.filter(repository=repository)
            .values("date__date")
            .annotate(commit_count=Count("id"))
            .order_by("date__date")
        )
        context["commit_frequency"] = commit_frequency

        # Top Contributors
        top_contributors = (
            Commit.objects.filter(repository=repository, author__isnull=False)
            .values("author__username")
            .annotate(commit_count=Count("id"))
            .order_by("-commit_count")[:10]
        )
        context["top_contributors"] = top_contributors

        # Commit Size Distribution
        size_distribution = Commit.objects.filter(repository=repository).aggregate(
            average_size=Avg("total"), max_size=Max("total"), min_size=Min("total")
        )
        context["size_distribution"] = size_distribution

        churn_data = Commit.objects.filter(repository=repository).aggregate(
            additions=Sum("additions"), deletions=Sum("deletions")
        )

        churn_rate = churn_data["additions"] + churn_data["deletions"]
        context["churn_rate"] = churn_rate

        # Commit Time Distribution
        time_distribution = (
            Commit.objects.filter(repository=repository)
            .annotate(hour=ExtractHour(F("commited_at")))
            .values("hour")
            .annotate(commit_count=Count("id"))
            .order_by("hour")
        )
        context["time_distribution"] = time_distribution

        return context


class CommitListView(LoginRequiredMixin, BaseListView):
    model = models.Commit
    list_display = ["sha", "repository", "author", "committer", "commited_at"]
    can_create = False
    can_edit = False
    actions = [
        ListAction("View Commit", "bi-eye", models.CommitAction.VIEW_COMMIT_DETAIL),
    ]

    def get_title(self):
        repository_name = models.Repository.objects.get(
            pk=self.kwargs["repository_id"]
        ).full_name
        return f'Showing commits for "{repository_name}"'

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(repository_id=self.kwargs["repository_id"])


class CommitDetailView(LoginRequiredMixin, BaseListView):
    model = models.CommitFile
    list_display = ["filename", "status", "additions", "deletions", "changes"]
    can_create = False
    can_edit = False

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(commit_id=self.kwargs["commit_id"])

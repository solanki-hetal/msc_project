import json
from datetime import timedelta
from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, F, Max, Min, Sum
from django.db.models.functions import ExtractHour, TruncDay
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, QueryDict, request
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import timedelta
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, TemplateView
from github import Github

from core.views import BaseCreateView, BaseListView, BaseUpdateView, ListAction
from tracker import forms, models
from tracker.services.repository import RepositorySyncService

from .models import Author, Commit, Repository


class DashboardView(TemplateView):
    template_name = "dashboard.html"

    _author = None

    def get_author(self):
        if self._author is False:
            return None
        if self._author is None:
            author_username = self.request.GET.get("author")
            if not author_username:
                self._author = False
            else:
                self._author = Author.objects.filter(username=author_username).first()
                if not self._author:
                    self._author = False
                    messages.error(self.request, "Author not found")
        return self._author

    def get_commit_queryset(self):
        author = self.get_author()
        if author:
            return Commit.objects.filter(author=author)
        return Commit.objects.all()

    def get_repository_queryset(self):
        author = self.get_author()
        if author:
            return Repository.objects.filter(commit__author=author).distinct()
        return Repository.objects.all()

    def get_generic_stats(self):
        data = {}
        # Total Repositories
        data["total_repositories"] = self.get_repository_queryset().count()

        # Total Commits
        data["total_commits"] = self.get_commit_queryset().count()

        # Top Language
        data["top_language"] = (
            self.get_repository_queryset()
            .values("language")
            .annotate(language_count=Count("language"))
            .order_by("-language_count")
            .first()
        )

        # Average Commits per Repository
        total_commits = self.get_commit_queryset().count()
        total_repositories = self.get_repository_queryset().count()
        print(total_commits, total_repositories)
        data["average_commits_per_repo"] = (
            total_commits / total_repositories if total_repositories else 0
        )

        # Recent Commits
        data["recent_commits"] = (
            self.get_commit_queryset().select_related("author").order_by("-date")[:10]
        )

        # Active Repositories
        last_30_days = timezone.now() - timedelta(days=30)
        data["active_repositories"] = (
            self.get_commit_queryset()
            .filter(date__gte=last_30_days)
            .values("repository__name")
            .annotate(commit_count=Count("id"))
            .order_by("-commit_count")[:5]
        )

        # Commit Frequency
        data["commit_frequency"] = (
            self.get_commit_queryset()
            .filter(date__gte=last_30_days)
            .annotate(date_day=TruncDay("date"))
            .values("date_day")
            .annotate(commit_count=Count("id"))
            .order_by("date_day")
        )

        # Churn Rate
        churn_rate = (
            self.get_commit_queryset()
            .filter(date__gte=last_30_days)
            .aggregate(
                total_additions=Sum("additions"), total_deletions=Sum("deletions")
            )
        )
        data["churn_rate"] = {
            "total_additions": churn_rate.get("total_additions", 0) or 0,
            "total_deletions": churn_rate.get("total_deletions", 0) or 0,
        }

        # Commits by Language
        data["commits_by_language"] = (
            self.get_repository_queryset()
            .values("language")
            .annotate(commit_count=Count("commit"))
            .order_by("-commit_count")
        )

        # Repository Comparison
        data["repository_comparison"] = (
            self.get_repository_queryset()
            .annotate(
                total_commits=Count("commit"),
                total_contributors=Count("commit__author", distinct=True),
                churn_rate=Sum("commit__additions") + Sum("commit__deletions"),
            )
            .values("name", "total_commits", "total_contributors", "churn_rate")
            .order_by("-total_commits")
        )

        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_generic_stats())
        return context


class TokenCreateView(LoginRequiredMixin, BaseCreateView):
    form_class = forms.TokenForm
    model = models.GitToken
    success_url = reverse_lazy("tracker:gittoken_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TokenEditView(LoginRequiredMixin, BaseUpdateView):
    form_class = forms.TokenForm
    model = models.GitToken
    success_url = reverse_lazy("tracker:gittoken_list")

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class TokenListView(LoginRequiredMixin, BaseListView):
    model = models.GitToken
    create_button_label = "Create Token"
    list_display = ["label", "service", "is_active"]
    can_delete = True
    searchable_fields = [
        "label",
    ]
    order_by_choices = [
        ("label", "Label"),
        ("is_active", "Active"),
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.has_perm("can_view_all_git_tokens"):
            queryset = queryset.filter(user=self.request.user)
        return queryset


@login_required
def delete_token(request: HttpRequest, pk: int):
    token = models.GitToken.objects.get(pk=pk)
    if request.user == token.user or request.user.has_perm("can_delete_all_git_tokens"):
        messages.success(request, f"Token {token.label} deleted successfully.")
        token.delete()
    else:
        messages.error(request, "You do not have permission to delete this token")
    return redirect("tracker:gittoken_list")


class RepositoryListView(LoginRequiredMixin, BaseListView):
    model = models.Repository
    list_display = [
        "name",
        "owner",
        "private",
        "language",
        "default_branch",
        "last_synced_at",
    ]
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
    searchable_fields = ["name", "owner__username", "description", "language"]
    order_by_choices = [
        ("name", "Name"),
        ("created_at", "Created At"),
        ("updated_at", "Updated At"),
        ("pushed_at", "Pushed At"),
        ("last_synced_at", "Last Synced At"),
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.has_perm("can_view_all_repositories"):
            return queryset
        return queryset.filter(users=self.request.user)


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

        context["commit_count"] = Commit.objects.filter(repository=repository).count()

        # Top Contributors
        top_contributors = (
            Commit.objects.filter(repository=repository, author__isnull=False)
            .values("author__username")
            .annotate(commit_count=Count("id"))
            .order_by("-commit_count")
        )
        context["top_contributors"] = top_contributors
        context["contributors_count"] = len(top_contributors)

        # Commit Size Distribution
        size_distribution = Commit.objects.filter(repository=repository).aggregate(
            average_size=Avg("total"), max_size=Max("total"), min_size=Min("total")
        )
        context["size_distribution"] = size_distribution

        churn_data = Commit.objects.filter(repository=repository).aggregate(
            additions=Sum("additions"), deletions=Sum("deletions")
        )

        churn_rate = (churn_data.get("additions") or 0) + (
            churn_data.get("deletions") or 0
        )
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
    list_display = [
        "repository",
        "message",
        "author",
        "committer",
        "commited_at",
        "additions",
        "deletions",
        "total",
    ]
    can_create = False
    can_edit = False
    actions = [
        ListAction("View Commit", "bi-eye", models.CommitAction.VIEW_COMMIT_DETAIL),
    ]
    searchable_fields = [
        "message",
        "repository__name",
        "author__username",
        "committer__username",
    ]

    order_by_choices = [
        # field name, Label
        ("commited_at", "Commit Date"),
        ("additions", "Additions"),
        ("deletions", "Deletions"),
        ("total", "Total Changes"),
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


class AnomalyListView(LoginRequiredMixin, BaseListView):
    model = models.Anomaly
    list_display = ["repository", "author", "anomaly_type", "description"]
    can_create = False
    can_edit = False
    can_delete = False


class NotificationListView(LoginRequiredMixin, BaseListView):
    model = models.Notification
    list_display = [
        "anomaly",
    ]
    can_create = False
    can_edit = False
    can_delete = False

    # def get_queryset(self):
    #     return self.model.objects.filter(instructor=self.request.user)


@csrf_exempt
def webhook_listener_view(request: HttpRequest):
    event = request.headers.get("X-GitHub-Event", "")
    hook_id = int(request.headers.get("X-GitHub-Hook-ID", ""))
    if not event:
        raise Exception("Event not found")
    if not hook_id:
        raise Exception("Hook ID not found")
    repository = Repository.objects.filter(webhook_id=hook_id).first()
    if not repository:
        raise Exception("Repository not found")
    repository: Repository
    token = models.GitToken.objects.filter(
        user__in=repository.users.all(), is_active=True
    ).first()
    if not token:
        raise Exception("No active token found")
    client = Github(token.token)
    git_repository = client.get_repo(repository.full_name)
    data = json.loads(request.body.decode("utf-8"))
    current_branch = data.get("ref").split("/")[2]
    if repository.default_branch != current_branch:
        raise Exception("Tracking branch does not match")
    sync_service = RepositorySyncService(repository=git_repository, repo_obj=repository)
    sync_service.fetch_commits()
    return HttpResponse("OK")

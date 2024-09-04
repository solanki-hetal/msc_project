from django.contrib import admin
from tracker import models

# Register your models here.


@admin.register(models.GitToken)
class GitTokenAdmin(admin.ModelAdmin):
    list_display = ["service", "label", "is_active"]
    list_filter = ["service", "is_active"]
    search_fields = ["label", "service"]


@admin.register(models.Repository)
class GitRepositoryAdmin(admin.ModelAdmin):
    list_display = ["name", "owner","webhook_id", "created_at"]
    list_filter = [
        "owner",
        "private",
        "language",
        "license",
    ]
    search_fields = ["name", "owner"]


@admin.register(models.Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["username", "git_id", "avatar_url", "html_url"]
    search_fields = ["username", "git_id"]
    list_filter = ["username", "git_id"]


@admin.register(models.Commit)
class CommitAdmin(admin.ModelAdmin):
    list_display = ["sha", "repository", "author", "committer", "commited_at"]
    list_filter = ["repository", "author", "committer"]
    search_fields = ["sha", "repository", "author", "committer"]


@admin.register(models.Anomaly)
class AnomalyAdmin(admin.ModelAdmin):
    list_display = ["repository", "author", "anomaly_type", "description"]
    list_filter = ["anomaly_type"]
    search_fields = ["repository", "author", "description"]

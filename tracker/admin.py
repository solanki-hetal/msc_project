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
    list_display = ["name", "owner", "parent", "source", "created_at"]
    list_filter = [
        "owner",
        "private",
        "language",
        "license",
    ]
    search_fields = ["name", "owner"]

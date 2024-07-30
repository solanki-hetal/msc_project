from django.conf import settings
from django.db import models
from django.urls import reverse

# Create your models here.


class GitToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.TextField()
    service = models.CharField(
        max_length=20,
        choices=[
            ("github", "GitHub"),
            ("gitlab", "Gitlab"),
        ],
    )

    def get_absolute_url(self):
        return reverse("tracker:token_edit", kwargs={"pk": self.pk})


class Repository(models.Model):
    token = models.ForeignKey(GitToken, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    url = models.URLField()
    description = models.TextField(null=True, blank=True)
    owner = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    last_fetched = models.DateTimeField(null=True, blank=True)


class Commit(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    sha = models.CharField(max_length=255)
    message = models.TextField()
    date = models.DateTimeField()
    author = models.CharField(max_length=255)
    additions = models.BigIntegerField(default=0)
    deletions = models.BigIntegerField(default=0)
    total = models.BigIntegerField(default=0)
    files = models.CharField(max_length=255)


class CommitAnalysis(models.Model):
    commit = models.ForeignKey(Commit, on_delete=models.CASCADE)
    quality = models.IntegerField()
    commit_type = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

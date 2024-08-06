from django.conf import settings
from django.db import models
from django.urls import reverse

# Create your models here.


class GitToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    label = models.CharField(max_length=255)
    token = models.TextField()
    is_active = models.BooleanField(default=True)
    service = models.CharField(
        max_length=20,
        choices=[
            ("github", "GitHub"),
            ("gitlab", "Gitlab"),
        ],
    )

    def get_absolute_url(self):
        return reverse("tracker:token_edit", kwargs={"pk": self.pk})

    def __str__(self) -> str:
        return self.label


class Author(models.Model):
    username = models.CharField(max_length=255, unique=True)
    git_id = models.BigIntegerField(unique=True)
    avatar_url = models.URLField()
    html_url = models.URLField()

    def __str__(self) -> str:
        return self.username


class Repository(models.Model):
    git_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=255)
    full_name = models.TextField()
    owner = models.ForeignKey(Author, on_delete=models.PROTECT)
    private = models.BooleanField(default=False)
    html_url = models.URLField()
    description = models.TextField(null=True, blank=True)
    language = models.CharField(max_length=255, null=True, blank=True)
    license = models.CharField(max_length=255, null=True, blank=True)
    default_branch = models.CharField(max_length=255)
    parent = models.ForeignKey(
        "self", on_delete=models.PROTECT, related_name="children", null=True, blank=True
    )
    source = models.ForeignKey(
        "self", on_delete=models.PROTECT, related_name="+", null=True, blank=True
    )
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    pushed_at = models.DateTimeField(null=True, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.full_name
    class Meta:
        verbose_name_plural = "Repositories"
        


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

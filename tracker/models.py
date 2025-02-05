from enum import Enum
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
        return reverse("tracker:gittoken_edit", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse("tracker:gittoken_delete", kwargs={"pk": self.pk})

    def __str__(self) -> str:
        return self.label

    class Meta:
        permissions = [
            ("can_view_all_git_tokens", "Can view all git tokens"),
            ("can_delete_all_git_tokens", "Can delete all git tokens"),
        ]


class Author(models.Model):
    username = models.CharField(max_length=255, unique=True)
    git_id = models.BigIntegerField(unique=True)
    avatar_url = models.URLField()
    html_url = models.URLField()

    def __str__(self) -> str:
        return self.username


class RepositoryAction(Enum):
    COMMITS = "commits"
    ANALYSIS = "analysis"


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
    webhook_id = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    pushed_at = models.DateTimeField(null=True, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="repositories"
    )

    def __str__(self) -> str:
        return self.full_name

    def get_action_url(self, action):
        if action == RepositoryAction.COMMITS:
            return self.get_commit_url()
        if action == RepositoryAction.ANALYSIS:
            return self.get_analysis_url()
        return self.get_absolute_url()

    def get_commit_url(self):
        return reverse("tracker:commit_list", kwargs={"repository_id": self.pk})

    def get_analysis_url(self):
        return reverse("tracker:repository_analysis", kwargs={"pk": self.pk})

    class Meta:
        verbose_name_plural = "Repositories"
        permissions = [("can_view_all_repositories", "Can view all repositories")]
        unique_together = (
            (
                "git_id",
                "owner",
            ),
        )


class CommitAction(Enum):
    VIEW_COMMIT_DETAIL = "view_commit_detail"


class Commit(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    sha = models.CharField(max_length=255)
    message = models.TextField()
    date = models.DateTimeField()
    commited_at = models.DateTimeField()
    author = models.ForeignKey(Author, on_delete=models.PROTECT, null=True, blank=True)
    committer = models.ForeignKey(
        Author, on_delete=models.PROTECT, related_name="+", null=True, blank=True
    )
    url = models.URLField()
    additions = models.BigIntegerField(default=0)
    deletions = models.BigIntegerField(default=0)
    total = models.BigIntegerField(default=0)

    def get_action_url(self, action):
        if action == CommitAction.VIEW_COMMIT_DETAIL:
            return self.get_detail_url()
        return None

    def get_detail_url(self):
        return reverse(
            "tracker:commit_detail",
            kwargs={"repository_id": self.repository.pk, "commit_id": self.pk},
        )

    def __str__(self) -> str:
        return f"{self.repository.full_name} - {self.message}"

    class Meta:
        verbose_name_plural = "Commits"
        unique_together = (("repository", "sha"),)
        ordering = ["-commited_at"]


class CommitFile(models.Model):
    commit = models.ForeignKey(Commit, on_delete=models.CASCADE)
    filename = models.TextField()
    status = models.CharField(max_length=50)
    additions = models.BigIntegerField(default=0)
    deletions = models.BigIntegerField(default=0)
    changes = models.BigIntegerField(default=0)
    patch = models.TextField(null=True, blank=True)
    
    def __str__(self) -> str:
        return self.filename

    class Meta:
        verbose_name_plural = "Commit Files"
        unique_together = (("commit", "filename"),)


class CommitAnalysis(models.Model):
    commit = models.ForeignKey(Commit, on_delete=models.CASCADE)
    quality = models.IntegerField()
    commit_type = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Quality: {self.quality}, Type: {self.commit_type}"


class Anomaly(models.Model):
    ANOMALY_TYPES = (
        ("infrequent_commits", "Infrequent Commits"),
        ("mass_commits", "Mass Commits at Odd Times"),
        ("plagiarism", "Potential Plagiarism"),
    )

    repository = models.ForeignKey("Repository", on_delete=models.CASCADE)
    author = models.ForeignKey(
        "Author", on_delete=models.CASCADE, null=True, blank=True
    )
    anomaly_type = models.CharField(max_length=50, choices=ANOMALY_TYPES)
    detected_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self) -> str:
        return "{} - {}".format(self.get_anomaly_type_display(), self.description)

    class Meta:
        verbose_name_plural = "Anomalies"


class Notification(models.Model):
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    anomaly = models.ForeignKey("Anomaly", on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.instructor.username} - {self.anomaly}"

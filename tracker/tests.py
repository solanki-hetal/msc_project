import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from tracker.models import (
    Anomaly,
    Author,
    Commit,
    CommitAnalysis,
    CommitFile,
    GitToken,
    Notification,
    Repository,
)
from tracker.services.repository import RepositorySyncService

User = get_user_model()


class GitTokenTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.git_token = GitToken.objects.create(
            user=self.user, label="Test Token", token="abcd1234", service="github"
        )

    def test_git_token_str(self):
        self.assertEqual(str(self.git_token), "Test Token")

    def test_git_token_get_absolute_url(self):
        self.assertEqual(
            self.git_token.get_absolute_url(),
            reverse("tracker:gittoken_edit", kwargs={"pk": self.git_token.pk}),
        )

    def test_git_token_get_delete_url(self):
        self.assertEqual(
            self.git_token.get_delete_url(),
            reverse("tracker:gittoken_delete", kwargs={"pk": self.git_token.pk}),
        )


class AuthorTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            username="author1",
            git_id=123456789,
            avatar_url="http://example.com/avatar.jpg",
            html_url="http://example.com/profile",
        )

    def test_author_str(self):
        self.assertEqual(str(self.author), "author1")


class RepositoryTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            username="author1",
            git_id=123456789,
            avatar_url="http://example.com/avatar.jpg",
            html_url="http://example.com/profile",
        )
        self.repo = Repository.objects.create(
            git_id=987654321,
            name="Test Repo",
            full_name="author1/Test Repo",
            owner=self.author,
            private=False,
            html_url="http://example.com/repo",
            default_branch="main",
        )

    def test_repository_str(self):
        self.assertEqual(str(self.repo), "author1/Test Repo")

    def test_repository_get_commit_url(self):
        self.assertEqual(
            self.repo.get_commit_url(),
            reverse("tracker:commit_list", kwargs={"repository_id": self.repo.pk}),
        )

    def test_repository_get_analysis_url(self):
        self.assertEqual(
            self.repo.get_analysis_url(),
            reverse("tracker:repository_analysis", kwargs={"pk": self.repo.pk}),
        )


class CommitTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            username="author1",
            git_id=123456789,
            avatar_url="http://example.com/avatar.jpg",
            html_url="http://example.com/profile",
        )
        self.repo = Repository.objects.create(
            git_id=987654321,
            name="Test Repo",
            full_name="author1/Test Repo",
            owner=self.author,
            private=False,
            html_url="http://example.com/repo",
            default_branch="main",
        )
        self.commit = Commit.objects.create(
            repository=self.repo,
            sha="abcdef1234567890",
            message="Initial commit",
            date="2024-01-01T00:00:00Z",
            commited_at="2024-01-01T00:00:00Z",
            author=self.author,
            committer=self.author,
            url="http://example.com/commit",
            additions=10,
            deletions=2,
            total=12,
        )

    def test_commit_str(self):
        self.assertEqual(str(self.commit), "author1/Test Repo - Initial commit")

    def test_commit_get_detail_url(self):
        self.assertEqual(
            self.commit.get_detail_url(),
            reverse(
                "tracker:commit_detail",
                kwargs={"repository_id": self.repo.pk, "commit_id": self.commit.pk},
            ),
        )


class CommitFileTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            username="author1",
            git_id=123456789,
            avatar_url="http://example.com/avatar.jpg",
            html_url="http://example.com/profile",
        )
        self.repo = Repository.objects.create(
            git_id=987654321,
            name="Test Repo",
            full_name="author1/Test Repo",
            owner=self.author,
            private=False,
            html_url="http://example.com/repo",
            default_branch="main",
        )
        self.commit = Commit.objects.create(
            repository=self.repo,
            sha="abcdef1234567890",
            message="Initial commit",
            date="2024-01-01T00:00:00Z",
            commited_at="2024-01-01T00:00:00Z",
            author=self.author,
            committer=self.author,
            url="http://example.com/commit",
            additions=10,
            deletions=2,
            total=12,
        )
        self.commit_file = CommitFile.objects.create(
            commit=self.commit,
            filename="file.py",
            status="modified",
            additions=5,
            deletions=1,
            changes=6,
            patch="--- a/file.py\n+++ b/file.py\n@@ -1,2 +1,2 @@\n",
        )

    def test_commit_file_str(self):
        self.assertEqual(str(self.commit_file), "file.py")


class CommitAnalysisTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            username="author1",
            git_id=123456789,
            avatar_url="http://example.com/avatar.jpg",
            html_url="http://example.com/profile",
        )
        self.repo = Repository.objects.create(
            git_id=987654321,
            name="Test Repo",
            full_name="author1/Test Repo",
            owner=self.author,
            private=False,
            html_url="http://example.com/repo",
            default_branch="main",
        )
        self.commit = Commit.objects.create(
            repository=self.repo,
            sha="abcdef1234567890",
            message="Initial commit",
            date="2024-01-01T00:00:00Z",
            commited_at="2024-01-01T00:00:00Z",
            author=self.author,
            committer=self.author,
            url="http://example.com/commit",
            additions=10,
            deletions=2,
            total=12,
        )
        self.analysis = CommitAnalysis.objects.create(
            commit=self.commit, quality=80, commit_type="feature"
        )

    def test_commit_analysis_str(self):
        self.assertEqual(
            str(self.analysis),
            f"Quality: {self.analysis.quality}, Type: {self.analysis.commit_type}",
        )


class AnomalyTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            username="author1",
            git_id=123456789,
            avatar_url="http://example.com/avatar.jpg",
            html_url="http://example.com/profile",
        )
        self.repo = Repository.objects.create(
            git_id=987654321,
            name="Test Repo",
            full_name="author1/Test Repo",
            owner=self.author,
            private=False,
            html_url="http://example.com/repo",
            default_branch="main",
        )
        self.anomaly = Anomaly.objects.create(
            repository=self.repo,
            author=self.author,
            anomaly_type="infrequent_commits",
            description="Fewer commits than usual",
        )

    def test_anomaly_str(self):
        self.assertEqual(
            str(self.anomaly), "Infrequent Commits - Fewer commits than usual"
        )


class NotificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.author = Author.objects.create(
            username="author1",
            git_id=123456789,
            avatar_url="http://example.com/avatar.jpg",
            html_url="http://example.com/profile",
        )
        self.repo = Repository.objects.create(
            git_id=987654321,
            name="Test Repo",
            full_name="author1/Test Repo",
            owner=self.author,
            private=False,
            html_url="http://example.com/repo",
            default_branch="main",
        )
        self.anomaly = Anomaly.objects.create(
            repository=self.repo,
            author=self.author,
            anomaly_type="infrequent_commits",
            description="Fewer commits than usual",
        )
        self.notification = Notification.objects.create(
            instructor=self.user, anomaly=self.anomaly
        )

    def test_notification_str(self):
        self.assertEqual(
            str(self.notification),
            f"Notification for {self.user.username} - {self.anomaly}",
        )


class GitTokenModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.token = GitToken.objects.create(
            user=self.user,
            label="testtoken",
            token="sometoken",
            is_active=True,
            service="github",
        )

    def test_git_token_str(self):
        self.assertEqual(str(self.token), "testtoken")

    def test_git_token_get_absolute_url(self):
        self.assertEqual(
            self.token.get_absolute_url(),
            reverse("tracker:gittoken_edit", kwargs={"pk": self.token.pk}),
        )

    def test_git_token_get_delete_url(self):
        self.assertEqual(
            self.token.get_delete_url(),
            reverse("tracker:gittoken_delete", kwargs={"pk": self.token.pk}),
        )


class AuthorModelTestCase(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            username="testauthor",
            git_id=12345,
            avatar_url="http://example.com/avatar.png",
            html_url="http://example.com",
        )

    def test_author_str(self):
        self.assertEqual(str(self.author), "testauthor")


class RepositoryModelTestCase(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            username="testauthor",
            git_id=12345,
            avatar_url="http://example.com/avatar.png",
            html_url="http://example.com",
        )
        self.repository = Repository.objects.create(
            git_id=67890,
            name="testrepo",
            full_name="testrepo/full",
            owner=self.author,
            private=False,
            html_url="http://example.com/repo",
            description="A test repository",
            language="Python",
            license="MIT",
            default_branch="main",
            webhook_id=1234,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            pushed_at=timezone.now(),
        )

    def test_repository_str(self):
        self.assertEqual(str(self.repository), "testrepo/full")

    def test_get_commit_url(self):
        self.assertEqual(
            self.repository.get_commit_url(),
            reverse(
                "tracker:commit_list", kwargs={"repository_id": self.repository.pk}
            ),
        )

    def test_get_analysis_url(self):
        self.assertEqual(
            self.repository.get_analysis_url(),
            reverse("tracker:repository_analysis", kwargs={"pk": self.repository.pk}),
        )


class CommitModelTestCase(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            username="testauthor",
            git_id=12345,
            avatar_url="http://example.com/avatar.png",
            html_url="http://example.com",
        )
        self.repository = Repository.objects.create(
            git_id=67890,
            name="testrepo",
            full_name="testrepo/full",
            owner=self.author,
            private=False,
            html_url="http://example.com/repo",
            description="A test repository",
            language="Python",
            license="MIT",
            default_branch="main",
            webhook_id=1234,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            pushed_at=timezone.now(),
        )
        self.commit = Commit.objects.create(
            repository=self.repository,
            sha="abcdef123456",
            message="Initial commit",
            date=timezone.now(),
            commited_at=timezone.now(),
            author=self.author,
            committer=self.author,
            url="http://example.com/commit",
            additions=10,
            deletions=5,
            total=15,
        )

    def test_commit_str(self):
        self.assertEqual(str(self.commit), "testrepo/full - Initial commit")

    def test_get_detail_url(self):
        self.assertEqual(
            self.commit.get_detail_url(),
            reverse(
                "tracker:commit_detail",
                kwargs={
                    "repository_id": self.repository.pk,
                    "commit_id": self.commit.pk,
                },
            ),
        )


class CommitFileModelTestCase(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            username="testauthor",
            git_id=12345,
            avatar_url="http://example.com/avatar.png",
            html_url="http://example.com",
        )
        self.repository = Repository.objects.create(
            git_id=67890,
            name="testrepo",
            full_name="testrepo/full",
            owner=self.author,
            private=False,
            html_url="http://example.com/repo",
            description="A test repository",
            language="Python",
            license="MIT",
            default_branch="main",
            webhook_id=1234,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            pushed_at=timezone.now(),
        )
        self.commit = Commit.objects.create(
            repository=self.repository,
            sha="abcdef123456",
            message="Initial commit",
            date=timezone.now(),
            commited_at=timezone.now(),
            author=self.author,
            committer=self.author,
            url="http://example.com/commit",
            additions=10,
            deletions=5,
            total=15,
        )
        self.commit_file = CommitFile.objects.create(
            commit=self.commit,
            filename="testfile.py",
            status="modified",
            additions=5,
            deletions=2,
            changes=7,
        )

    def test_commit_file_str(self):
        self.assertEqual(str(self.commit_file), "testfile.py")


class CommitAnalysisModelTestCase(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            username="testauthor",
            git_id=12345,
            avatar_url="http://example.com/avatar.png",
            html_url="http://example.com",
        )
        self.repository = Repository.objects.create(
            git_id=67890,
            name="testrepo",
            full_name="testrepo/full",
            owner=self.author,
            private=False,
            html_url="http://example.com/repo",
            description="A test repository",
            language="Python",
            license="MIT",
            default_branch="main",
            webhook_id=1234,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            pushed_at=timezone.now(),
        )
        self.commit = Commit.objects.create(
            repository=self.repository,
            sha="abcdef123456",
            message="Initial commit",
            date=timezone.now(),
            commited_at=timezone.now(),
            author=self.author,
            committer=self.author,
            url="http://example.com/commit",
            additions=10,
            deletions=5,
            total=15,
        )
        self.analysis = CommitAnalysis.objects.create(
            commit=self.commit, quality=80, commit_type="feature"
        )

    def test_commit_analysis_str(self):
        self.assertEqual(str(self.analysis), "Quality: 80, Type: feature")


class AnomalyModelTestCase(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            username="testauthor",
            git_id=12345,
            avatar_url="http://example.com/avatar.png",
            html_url="http://example.com",
        )
        self.repository = Repository.objects.create(
            git_id=67890,
            name="testrepo",
            full_name="testrepo/full",
            owner=self.author,
            private=False,
            html_url="http://example.com/repo",
            description="A test repository",
            language="Python",
            license="MIT",
            default_branch="main",
            webhook_id=1234,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            pushed_at=timezone.now(),
        )
        self.anomaly = Anomaly.objects.create(
            repository=self.repository,
            author=self.author,
            anomaly_type="mass_commits",
            description="High number of commits at odd times",
        )

    def test_anomaly_str(self):
        self.assertEqual(
            str(self.anomaly),
            "Mass Commits at Odd Times - High number of commits at odd times",
        )


class NotificationModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.author = Author.objects.create(
            username="testauthor",
            git_id=12345,
            avatar_url="http://example.com/avatar.png",
            html_url="http://example.com",
        )
        self.repository = Repository.objects.create(
            git_id=67890,
            name="testrepo",
            full_name="testrepo/full",
            owner=self.author,
            private=False,
            html_url="http://example.com/repo",
            description="A test repository",
            language="Python",
            license="MIT",
            default_branch="main",
            webhook_id=1234,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            pushed_at=timezone.now(),
        )
        self.anomaly = Anomaly.objects.create(
            repository=self.repository,
            author=self.author,
            anomaly_type="plagiarism",
            description="Potential plagiarism detected",
        )
        self.notification = Notification.objects.create(
            instructor=self.user, anomaly=self.anomaly
        )

    def test_notification_str(self):
        self.assertEqual(
            str(self.notification),
            f"Notification for {self.user.username} - {self.anomaly}",
        )


class DashboardViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")

    def test_dashboard_view(self):
        response = self.client.get(reverse("tracker:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard.html")

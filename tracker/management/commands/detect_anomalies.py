# detect_anomalies.py

from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Count, Q, Sum
from django.utils import timezone

from tracker.models import Anomaly, Author, Commit, Notification, Repository


class Command(BaseCommand):
    help = "Detects anomalous trends in commits and notifies instructors"

    def handle(self, *args, **options):
        self.stdout.write("Starting anomaly detection...")

        # Define timeframes
        now = timezone.now()
        last_week = now - timedelta(weeks=1)

        # Detect anomalies
        self.detect_infrequent_commits(last_week)
        self.detect_mass_commits_at_odd_times(last_week)
        self.detect_plagiarism_patterns(last_week)

        self.stdout.write("Anomaly detection completed.")

    def detect_infrequent_commits(self, last_week):
        # Detect repositories with infrequent commits
        infrequent_repos = Repository.objects.annotate(
            recent_commits=Count("commit", filter=Q(commit__date__gte=last_week))
        ).filter(
            recent_commits__lt=5
        )  # Threshold for infrequency

        for repo in infrequent_repos:
            description = (
                f"Repository '{repo.name}' has less than 5 commits in the last week."
            )
            anomaly = self.create_anomaly_entry(
                repo, None, "infrequent_commits", description
            )
            self.create_notification(anomaly, description)

    def detect_mass_commits_at_odd_times(self, last_week):
        # Detect mass commits at odd times (e.g., late night)
        mass_commits = (
            Commit.objects.filter(
                date__gte=last_week,
                date__hour__gte=0,  # Midnight to early morning
                date__hour__lt=6,
            )
            .values("author")
            .annotate(commit_count=Count("id"))
            .filter(commit_count__gte=10)
        )  # Threshold for mass commits

        for commit_info in mass_commits:
            author = Author.objects.get(id=commit_info["author"])
            description = f"Author '{author.username}' made {commit_info['commit_count']} commits during odd hours."
            anomaly = self.create_anomaly_entry(
                None, author, "mass_commits_odd_times", description
            )
            self.create_notification(anomaly, description)

    def detect_plagiarism_patterns(self, last_week):
        # Detect similar commit messages or code that may indicate plagiarism
        plagiarism_candidates = (
            Commit.objects.filter(date__gte=last_week)
            .values("message", "repository__name")
            .annotate(message_count=Count("message"))
            .filter(message_count__gte=5)
        )  # Threshold for similarity

        for candidate in plagiarism_candidates:
            repository = Repository.objects.get(name=candidate["repository__name"])
            description = f"Potential plagiarism detected in repository '{repository.name}' with commit message: '{candidate['message']}'."
            anomaly = self.create_anomaly_entry(
                repository, None, "plagiarism", description
            )
            self.create_notification(anomaly, description)

    def create_anomaly_entry(self, repository, author, anomaly_type, description):
        # Create an anomaly entry
        anomaly = Anomaly.objects.create(
            repository=repository,
            author=author,
            anomaly_type=anomaly_type,
            description=description,
        )
        return anomaly

    def create_notification(self, anomaly, message):
        # Create a notification entry for each instructor (assuming you have an 'instructors' group or similar)
        instructors = User.objects.filter(
            groups__name="Instructors"
        )  # Replace 'Instructors' with the actual group name
        for instructor in instructors:
            Notification.objects.create(
                user=instructor, anomaly=anomaly, message=message
            )
        self.stdout.write(
            self.style.SUCCESS(f"Notifications created for anomaly: {anomaly}")
        )

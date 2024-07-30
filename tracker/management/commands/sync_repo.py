from django.core.management.base import BaseCommand, CommandError
from tracker import models
from github import Github, GithubException


class Command(BaseCommand):
    help = "Sync repos locally"

    def print_file_details(self, file):
        """
        Print details of a file in a commit.
        """
        print(f"Status: {file.status}")
        print(f"Additions: {file.additions}")
        print(f"Deletions: {file.deletions}")
        print(f"Changes: {file.changes}")
        print(f"Patch: {file.patch}")
        print("------------------")
        print("------------------")
        print("------------------")

    def print_commit_details(self, commit):
        """
        Print details of a single commit including file changes.
        """
        print(f"Commit SHA: {commit.sha}")
        print(f"Author: {commit.commit.author.name}")
        print(f"Date: {commit.commit.author.date}")
        print(f"Message: {commit.commit.message}")
        print("Files changed:")

        # Fetching details of files changed in the commit
        for file in commit.files:
            self.print_file_details(file)
        print("---")

    def fetch_user_details(self, github_client):
        """
        Fetch and return the authenticated user details.
        """
        try:
            user = github_client.get_user()
            print(f"Authenticated as: {user.login}")
            return user
        except GithubException as e:
            print(f"Failed to fetch user details: {e}")
            return None

    def fetch_repositories(self, user):
        """
        Fetch and print repositories for the authenticated user.
        """
        try:
            repos = user.get_repos()
            print("Repositories:")
            for repo in repos:
                print(f"- {repo.name}")
            return repos
        except GithubException as e:
            print(f"Failed to fetch repositories: {e}")
            return []

    def fetch_commits(self, repository):
        """
        Fetch and print commits for a given repository.
        """
        try:
            commits = repository.get_commits()
            for commit in commits:
                self.print_commit_details(commit)
        except GithubException as e:
            print(f"Failed to fetch commits for repository {repository.name}: {e}")

    def handle(self, *args, **options):
        tokens = models.GitToken.objects.all()
        for token in tokens:
            github_client = Github(token.token)
            user = self.fetch_user_details(github_client)
            if user:
                repos = self.fetch_repositories(user)
                for repo in repos:
                    self.fetch_commits(repo)

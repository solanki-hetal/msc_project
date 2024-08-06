import json
import os
from django.core.management.base import BaseCommand, CommandError
from tracker import models
from github import Github, GithubException

from django.utils import timezone


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

    def insert_or_update_repository(self, repo, owners={}):
        """
        Insert or update a repository in the database.
        """
        if repo.owner.id not in owners:
            owner, _ = models.Author.objects.get_or_create(
                git_id=repo.owner.id,
                defaults={
                    "username": repo.owner.login,
                    "avatar_url": repo.owner.avatar_url,
                    "html_url": repo.owner.html_url,
                },
            )
            owners[repo.owner.id] = owner
        else:
            owner = owners[repo.owner.id]
        source, _ = (
            self.insert_or_update_repository(repo.source, owners)
            if repo.source
            else (None, None)
        )
        parent, _ = (
            self.insert_or_update_repository(repo.parent, owners)
            if repo.parent
            else (None, None)
        )
        return models.Repository.objects.update_or_create(
            git_id=repo.id,
            owner=owner,
            defaults={
                "name": repo.name,
                "full_name": repo.full_name,
                "private": repo.private,
                "html_url": repo.html_url,
                "description": repo.description,
                "language": repo.language,
                "license": repo.license,
                "default_branch": repo.default_branch,
                "source": source,
                "parent": parent,
                "created_at": repo.created_at,
                "updated_at": repo.updated_at,
                "pushed_at": repo.pushed_at,
                "last_synced_at": timezone.now(),
            },
        )

    def fetch_repositories(self, git_user, user):
        """
        Fetch and print repositories for the authenticated user.
        """
        try:
            _repos = git_user.get_repos()
            print("Repositories:")
            owners = {}
            repositories = []
            for repo in _repos:
                self.stdout.write(f"Syncing - {repo.name}", self.style.WARNING)
                repository, _ = self.insert_or_update_repository(repo, owners)
                repositories.append(repository)
                self.fetch_commits(repo)
                self.stdout.write(f"Synced - {repo.name}", self.style.SUCCESS)
                self.stdout.write("-------------------------------------------------")
                break
            user.repositories.set(repositories)
            return repositories
        except GithubException as e:
            self.stderr.write(f"Failed to fetch repositories: {e}")
            return []

    def fetch_commits(self, repository):
        """
        Fetch and print commits for a given repository.
        """
        try:
            commits = repository.get_commits()
            for commit in commits:
                # self.print_commit_details(commit)
                json.dump(
                    commit.raw_data,
                    open(os.path.join("commits", f"{commit.sha}.json"), "w"),
                    indent=4,
                )
        except GithubException as e:
            print(f"Failed to fetch commits for repository {repository.name}: {e}")

    def handle(self, *args, **options):
        tokens = models.GitToken.objects.filter(is_active=True)
        for token in tokens:
            github_client = Github(token.token)
            git_user = self.fetch_user_details(github_client)
            if git_user:
                repos = self.fetch_repositories(git_user, token.user)
                # for repo in repos:
                # self.fetch_commits(repo)

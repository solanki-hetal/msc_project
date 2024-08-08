import json
import os
from django.core.management.base import BaseCommand, CommandError
from tracker import models
from github import Github, GithubException

from django.utils import timezone


class Command(BaseCommand):
    help = "Sync repos locally"

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

    def insert_or_update_author(self, author, owners={}):
        if author.id not in owners:
            owner, _ = models.Author.objects.get_or_create(
                git_id=author.id,
                defaults={
                    "username": author.login,
                    "avatar_url": author.avatar_url,
                    "html_url": author.html_url,
                },
            )
            owners[author.id] = owner
        else:
            owner = owners[author.id]
        return owner

    def insert_or_update_repository(self, repo, owners={}):
        """
        Insert or update a repository in the database.
        """
        owner = self.insert_or_update_author(repo.owner, owners)
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
            owners = {}
            repositories = []
            for repo in _repos:
                self.stdout.write(f"Syncing - {repo.name}", self.style.WARNING)
                repository, _ = self.insert_or_update_repository(repo, owners)
                repositories.append(repository)
                commits = self.fetch_commits(repo, repository, owners)
                self.stdout.write(
                    f"Synced commits - {len(commits)}", self.style.SUCCESS
                )
                self.stdout.write(f"Synced - {repo.name}", self.style.SUCCESS)
                self.stdout.write("-------------------------------------------------")
            user.repositories.set(repositories)
            return repositories
        except GithubException as e:
            self.stderr.write(f"Failed to fetch repositories: {e}")
            return []

    def fetch_commits(self, repository, repo_obj, owners={}):
        """
        Fetch and print commits for a given repository.
        """
        try:
            git_commits = repository.get_commits()
            _commits = []
            for _commit in git_commits:
                author = (
                    self.insert_or_update_author(_commit.author, owners)
                    if _commit.author
                    else None
                )
                committer = (
                    self.insert_or_update_author(_commit.committer, owners)
                    if _commit.committer
                    else None
                )
                commit, _ = models.Commit.objects.update_or_create(
                    repository=repo_obj,
                    sha=_commit.sha,
                    defaults={
                        "message": _commit.commit.message,
                        "date": _commit.commit.author.date,
                        "commited_at": _commit.commit.committer.date,
                        "author": author,
                        "committer": committer,
                        "url": _commit.html_url,
                        "additions": _commit.stats.additions,
                        "deletions": _commit.stats.deletions,
                        "total": _commit.stats.total,
                    },
                )
                for file in _commit.files:
                    models.CommitFile.objects.update_or_create(
                        commit=commit,
                        filename=file.filename,
                        defaults={
                            "status": file.status,
                            "additions": file.additions,
                            "deletions": file.deletions,
                            "changes": file.changes,
                            "patch": file.patch,
                        },
                    )
                _commits.append(commit)
            return _commits
        except Exception as e:
            json.dump(_commit.raw_data, open("error.json", "w"), indent=2)
            raise CommandError(
                f"Failed to fetch commits for repository {repository.name}: {e}"
            )

    def handle(self, *args, **options):
        tokens = models.GitToken.objects.filter(is_active=True)
        for token in tokens:
            github_client = Github(token.token)
            git_user = self.fetch_user_details(github_client)
            if git_user:
                self.fetch_repositories(git_user, token.user)

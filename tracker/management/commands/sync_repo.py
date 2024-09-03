import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from github import Github, GithubException, Hook

from tracker import models
from tracker.services.repository import RepositorySyncService


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

    def insert_or_update_repository(self, token: models.GitToken, repo, owners={}):
        """
        Insert or update a repository in the database.
        """
        owner = self.insert_or_update_author(repo.owner, owners)
        source, _ = (
            self.insert_or_update_repository(token, repo.source, owners)
            if repo.source
            else (None, None)
        )
        parent, _ = (
            self.insert_or_update_repository(token, repo.parent, owners)
            if repo.parent
            else (None, None)
        )
        obj, created = models.Repository.objects.update_or_create(
            git_id=repo.id,
            owner=owner,
            token=token,
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
        if created:
            EVENTS = ["push"]
            # config = {"url": settings.WEBHOOK_URL, "content_type": "json"}
            config = {"url": 'https://webhook.site/97c88c05-1be5-401c-b7e7-b73af37641a5', "content_type": "json"}
            try:              
              hook: Hook = repo.create_hook(
                  "project_tracker_webhook",
                  config,
                  EVENTS,
                  active=True,
              )
              obj.webhook_id = hook.id
              obj.save()
            except Exception as e:
              self.stderr.write(f"Failed to create webhook for repo {obj.name}: {e}")
              
        return obj, created

    def fetch_repositories(
        self,
        token: models.GitToken,
        git_user
    ):
        """
        Fetch and print repositories for the authenticated user.
        """
        # try:
        _repos = git_user.get_repos()
        owners = {}
        repositories = []
        for repo in _repos:
            self.stdout.write(f"Syncing - {repo.name}", self.style.WARNING)
            repository, _ = self.insert_or_update_repository(token, repo, owners)
            repositories.append(repository)
            sync_service = RepositorySyncService(repository=repo,repo_obj=repository)
            commits = sync_service.fetch_commits(owners=owners)
            self.stdout.write(
                f"Synced commits - {len(commits)}", self.style.SUCCESS
            )
            self.stdout.write(f"Synced - {repo.name}", self.style.SUCCESS)
            self.stdout.write("-------------------------------------------------")
        token.user.repositories.set(repositories)
        return repositories
        # except GithubException as e:
        #     self.stderr.write(f"Failed to fetch repositories: {e}")
        #     return []

  
    def handle(self, *args, **options):
        tokens = models.GitToken.objects.filter(is_active=True)
        for token in tokens:
            github_client = Github(token.token)
            git_user = self.fetch_user_details(github_client)
            if git_user:
                self.fetch_repositories(token, git_user)

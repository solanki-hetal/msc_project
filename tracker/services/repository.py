import json

from django.conf import settings
from django.core.management.base import CommandError
from django.utils import timezone
from github import Hook, Repository

from tracker import models


class RepositorySyncService:

    repository: Repository
    repo_obj: models.Repository

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
            config = {"url": settings.WEBHOOK_URL, "content_type": "json"}
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

    def fetch_commits(self, owners={}):
        """
        Fetch and print commits for a given repository.
        """
        try:
            git_commits = self.repository.get_commits()
            _commits = []
            for _commit in git_commits:
                author = (
                    self.insert_or_update_author(_commit.author, self.owners)
                    if _commit.author
                    else None
                )
                committer = (
                    self.insert_or_update_author(_commit.committer, owners)
                    if _commit.committer
                    else None
                )
                commit, _ = models.Commit.objects.update_or_create(
                    repository=self.repo_obj,
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
                f"Failed to fetch commits for repository {self.repo_obj.name}: {e}"
            )

    def __init__(self, repository: Repository, repo_obj: models.Repository, owners={}):
        self.repository = repository
        self.repo_obj = repo_obj
        self.owners = owners


# self.repository = repository

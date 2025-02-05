# Generated by Django 5.0.7 on 2024-08-08 13:56

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0009_remove_repository_user_repository_users'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='commit',
            options={'permissions': [('can_view_all_commits', 'Can view all commits')], 'verbose_name_plural': 'Commits'},
        ),
        migrations.AlterModelOptions(
            name='gittoken',
            options={'permissions': [('can_view_all_git_tokens', 'Can view all git tokens')]},
        ),
        migrations.AlterModelOptions(
            name='repository',
            options={'permissions': [('can_view_all_repositories', 'Can view all repositories')], 'verbose_name_plural': 'Repositories'},
        ),
        migrations.AlterUniqueTogether(
            name='commit',
            unique_together={('repository', 'sha')},
        ),
        migrations.AddField(
            model_name='commit',
            name='commited_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 8, 13, 56, 19, 956033, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='commit',
            name='committer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='tracker.author'),
        ),
        migrations.AddField(
            model_name='commit',
            name='url',
            field=models.URLField(default='https://url.com'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='commit',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tracker.author'),
        ),
        migrations.RemoveField(
            model_name='commit',
            name='files',
        ),
        migrations.CreateModel(
            name='CommitFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.TextField()),
                ('status', models.CharField(max_length=50)),
                ('additions', models.BigIntegerField(default=0)),
                ('deletions', models.BigIntegerField(default=0)),
                ('changes', models.BigIntegerField(default=0)),
                ('patch', models.TextField()),
                ('commit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.commit')),
            ],
            options={
                'verbose_name_plural': 'Commit Files',
                'unique_together': {('commit', 'filename')},
            },
        ),
    ]

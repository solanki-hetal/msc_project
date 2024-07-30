# Generated by Django 5.0.7 on 2024-07-30 12:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Commit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sha', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('date', models.DateTimeField()),
                ('author', models.CharField(max_length=255)),
                ('additions', models.BigIntegerField(default=0)),
                ('deletions', models.BigIntegerField(default=0)),
                ('total', models.BigIntegerField(default=0)),
                ('files', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='CommitAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quality', models.IntegerField()),
                ('commit_type', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('commit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.commit')),
            ],
        ),
        migrations.CreateModel(
            name='GitToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.TextField()),
                ('service', models.CharField(choices=[('github', 'GitHub'), ('gitlab', 'Gitlab')], max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('url', models.URLField()),
                ('description', models.TextField(blank=True, null=True)),
                ('owner', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_fetched', models.DateTimeField(blank=True, null=True)),
                ('token', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.gittoken')),
            ],
        ),
        migrations.AddField(
            model_name='commit',
            name='repository',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.repository'),
        ),
    ]

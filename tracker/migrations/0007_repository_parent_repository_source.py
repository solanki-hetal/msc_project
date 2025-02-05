# Generated by Django 5.0.7 on 2024-08-06 14:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0006_alter_repository_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='children', to='tracker.repository'),
        ),
        migrations.AddField(
            model_name='repository',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='tracker.repository'),
        ),
    ]

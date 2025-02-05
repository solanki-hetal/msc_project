# Generated by Django 5.0.7 on 2024-09-02 18:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0014_rename_details_anomaly_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='token',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tracker.gittoken'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='repository',
            unique_together={('token', 'git_id', 'token')},
        ),
    ]

# Generated by Django 5.0.7 on 2024-09-02 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0015_repository_token_alter_repository_unique_together'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='anomaly',
            options={'verbose_name_plural': 'Anomalies'},
        ),
        migrations.AddField(
            model_name='repository',
            name='webhook_id',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]

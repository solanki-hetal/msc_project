# Generated by Django 5.0.7 on 2024-08-06 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0005_author_alter_repository_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repository',
            name='created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

# Generated by Django 5.1.4 on 2024-12-12 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0003_alter_profile_experience_alter_profile_github_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobpreference',
            name='desired_roles',
            field=models.TextField(blank=True, help_text='Comma-separated roles', null=True),
        ),
        migrations.AlterField(
            model_name='jobpreference',
            name='salary_range',
            field=models.TextField(blank=True, help_text='Comma-separated salary range', null=True),
        ),
    ]

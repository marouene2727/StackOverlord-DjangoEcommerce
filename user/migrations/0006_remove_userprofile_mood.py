# Generated by Django 4.2 on 2024-10-25 00:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_userprofile_mood'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='mood',
        ),
    ]
# Generated by Django 4.2 on 2024-10-25 00:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_remove_userprofile_face_encoding'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='mood',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
# Generated by Django 4.2 on 2024-10-23 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_userprofile_address_userprofile_birth_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='face_encoding',
            field=models.TextField(default=''),
        ),
    ]

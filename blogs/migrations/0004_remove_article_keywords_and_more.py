# Generated by Django 5.1.1 on 2024-10-10 18:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0003_article_keywords_article_meta_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='keywords',
        ),
        migrations.RemoveField(
            model_name='article',
            name='meta_description',
        ),
    ]

# Generated by Django 5.1.1 on 2024-10-12 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0005_comment_moderated'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='sentiment_label',
            field=models.CharField(default='NEUTRAL', max_length=10),
        ),
        migrations.AddField(
            model_name='comment',
            name='sentiment_score',
            field=models.FloatField(default=0.0),
        ),
    ]
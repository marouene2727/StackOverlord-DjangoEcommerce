# Generated by Django 5.1.1 on 2024-10-05 16:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='nom',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='prix',
            new_name='price',
        ),
    ]

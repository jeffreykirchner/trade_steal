# Generated by Django 3.2.11 on 2022-01-13 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0099_remove_parameters_test_email_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionplayer',
            name='email',
            field=models.EmailField(blank=True, max_length=100, verbose_name='Email Address'),
        ),
    ]
# Generated by Django 4.1.3 on 2022-11-29 22:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0118_remove_sessionplayer_unique_email_session_player'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='sessionplayer',
            name='production_total_equals_100',
        ),
    ]

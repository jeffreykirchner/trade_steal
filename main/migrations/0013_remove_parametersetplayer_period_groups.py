# Generated by Django 3.2.8 on 2021-10-22 20:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_parametersetplayergroup'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parametersetplayer',
            name='period_groups',
        ),
    ]
